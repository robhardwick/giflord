import re
import logging
import hashlib
import urllib2
import time

from djangoappengine.storage import BlobstoreUploadedFile
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import files
from google.appengine.api import images
from google.appengine.api import taskqueue

import settings
from django.db import models

import mechanize
from BeautifulSoup import BeautifulSoup

class GifManager(models.Manager):
    def queue(self):
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)

        for reddit in ['pics', 'lol', 'wtf', 'gifs', 'trees']:
            url = 'http://www.reddit.com/r/' + reddit
            taskqueue.add(queue_name='crawl', url='/task/crawl', params={'url': url})

    def crawl(self, url):
        logging.info('Fetching ' + url)
        response = self.browser.open(url, timeout=10)

        doc = BeautifulSoup(response.get_data())
        for container in doc.findAll('div', {'class': re.compile(r'\bentry\b')}):
            link = container.find('a', {
                'class': re.compile(r'\btitle\b'),
                'href': re.compile(r'\.gif$')
            })
            if link:
                image_url = link['href'].strip()
                if Gif.objects.filter(url=image_url).count() > 0:
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

        gif = Gif()
        gif.url = url
        gif.referrer = referrer
        gif.digest = md5.hexdigest()

        if Gif.objects.filter(digest=gif.digest).count() > 0:
            logging.info('Skipping (Hash Exists)')
            return

        blob_key = None
        while not blob_key: 
            time.sleep(1) 
            blob_key = files.blobstore.get_blob_key(file_name)

        blobFile = BlobstoreUploadedFile(BlobInfo(blob_key), charset='utf-8')
        gif.image.save('image.gif', blobFile)
        gif.width = gif.image.width
        gif.height = gif.image.height

        gif.thumb_url = images.get_serving_url(blob_key, settings.THUMB_SIZE)

        ratio = min(settings.THUMB_SIZE/float(gif.width), settings.THUMB_SIZE/float(gif.height))
        gif.thumb_width = int(gif.width * ratio)
        gif.thumb_height = int(gif.height * ratio)
        gif.save()

        gif.url = '/image/' + str(gif.id) + '.gif'
        gif.save()

        logging.info('Successfully Added')

class Gif(models.Model):
    image = models.ImageField(upload_to='images/%Y/%m/%d/%H/%M/%S/')
    url = models.CharField(max_length=64)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    thumb_url = models.CharField(max_length=64)
    thumb_width = models.IntegerField(default=0)
    thumb_height = models.IntegerField(default=0)
    url = models.CharField(max_length=1024)
    referrer = models.CharField(max_length=1024)
    digest = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)
    objects = GifManager()

