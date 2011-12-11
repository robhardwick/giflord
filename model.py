import os
import logging
import hashlib
import urllib2
import time
import re

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.api import images
from google.appengine.api import taskqueue

import mechanize
from BeautifulSoup import BeautifulSoup

import settings

class GifManager:
    def queue(self):
        for reddit in ['pics', 'lol', 'wtf', 'trees', 'gifs']:
            url = 'http://www.reddit.com/r/' + reddit
            taskqueue.add(queue_name='crawl', url='/task/crawl', params={'url': url})

    def crawl(self, url):
        logging.info('Fetching ' + url)
        browser = mechanize.Browser()
        browser.set_handle_robots(False)

        response = browser.open(url, timeout=settings.CRAWL_TIMEOUT)

        doc = BeautifulSoup(response.get_data())
        for container in doc.findAll('div', {'class': re.compile(r'\bentry\b')}):
            link = container.find('a', {
                'class': re.compile(r'\btitle\b'),
                'href': re.compile(r'\.gif$')
            })
            if link:
                image_url = link['href'].strip()
                if gif_gif.all().filter('url =', image_url).count() > 0:
                    continue
                logging.info('Queueing ' + image_url)
                taskqueue.add(queue_name='fetch', url='/task/fetch', params={
                    'url': image_url,
                    'referrer': url
                })

    def fetch(self, url, referrer):
        logging.info('Fetching %s...' % (url))
        try:
            remote = urllib2.urlopen(url, None, 10)
        except urllib2.URLError:
            logging.error('Skipping (Invalid URL)')
        else:
            self.add_image(url, referrer, remote)
            remote.close()

    def add_image(self, url, referrer, remote):
        md5 = hashlib.md5()

        file_name = files.blobstore.create(mime_type='image/gif')
        with files.open(file_name, 'a') as f:
            while True:
                chunk = remote.read(2**10)
                if not chunk:
                    break
                f.write(chunk)
                md5.update(chunk)

        files.finalize(file_name)

        gif = gif_gif()
        gif.url = url
        gif.referrer = referrer
        gif.digest = md5.hexdigest()

        if gif_gif.all().filter('digest =', gif.digest).count() > 0:
            logging.info('Skipping (Hash Exists)')
            return

        blob_key = None
        while not blob_key: 
            time.sleep(1) 
            blob_key = files.blobstore.get_blob_key(file_name)

        header = blobstore.fetch_data(blob_key, 0, 50000)
        image = images.Image(image_data=header)

        gif.image = str(blob_key)
        gif.width = image.width
        gif.height = image.height
        gif.size = image.size

        gif.thumb_url = images.get_serving_url(blob_key, settings.THUMB_SIZE)

        ratio = min(settings.THUMB_SIZE/float(gif.width), settings.THUMB_SIZE/float(gif.height))
        gif.thumb_width = int(gif.width * ratio)
        gif.thumb_height = int(gif.height * ratio)

        gif.put()
        logging.info('Successfully Added')

    def updateV2(self, gif):
        image = gif.image.strip()
        r = r'^.*images/\d{4,4}/\d{2,2}/\d{2,2}/\d{2,2}/\d{2,2}/\d{2,2}/image\.gif$'
        if re.match(r, image):
            image = image[:-37]
            info = blobstore.BlobInfo.get(image)
            gif.image = str(info.key())
            gif.put()
            logging.info('Updated V2 ' + gif.image)

    def updateV3(self, gif):
        self.updateV2(gif)
        if gif.size is None:
            image = blobstore.BlobInfo.get(gif.image)
            gif.size = image.size
            gif.put()
            logging.info('Updated V3 ' + gif.image)

class gif_gif(db.Model):
    image = db.StringProperty()
    width = db.IntegerProperty()
    height = db.IntegerProperty()
    size = db.IntegerProperty()
    thumb_url = db.StringProperty()
    thumb_width = db.IntegerProperty()
    thumb_height = db.IntegerProperty()
    url = db.StringProperty()
    referrer = db.StringProperty()
    digest = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    objects = GifManager()

