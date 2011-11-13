import re
import logging
import hashlib
import urllib2
import time

from djangoappengine.storage import BlobstoreUploadedFile
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import files
from google.appengine.api import images

import settings
from django.db import models

import mechanize
from BeautifulSoup import BeautifulSoup

class Gif(models.Model):
    image = models.ImageField(upload_to='images/%Y/%m/%d/%H/%M/%S/')
    url = models.CharField(max_length=64)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    thumb_url = models.CharField(max_length=64)
    thumb_width = models.IntegerField(default=0)
    thumb_height = models.IntegerField(default=0)
    href = models.CharField(max_length=1024)
    referrer = models.CharField(max_length=1024)
    digest = models.CharField(max_length=32)
    created = models.DateTimeField(auto_now_add=True)

class GifQueueManager(models.Manager):
    def queue(self):
        self.browser = mechanize.Browser()
        self.browser.set_handle_robots(False)

        for reddit in ['pics', 'lol', 'wtf', 'gifs']:
            href = 'http://www.reddit.com/r/' + reddit

            logging.info('Fetching ' + href)
            response = self.browser.open(href, timeout=10)

            doc = BeautifulSoup(response.get_data())
            self.process_doc(href, doc)

    def process_doc(self, href, doc):
        for container in doc.findAll('div', {'class': re.compile(r'\bentry\b')}):
            link = container.find('a', {
                'class': re.compile(r'\btitle\b'),
                'href': re.compile(r'\.gif$')
            })
            if link:
                logging.info('Queueing ' + link['href'])
                self.queue_image(link['href'], href)

    def queue_image(self, image_href, doc_href):
        image_href = image_href.strip()
        item = GifQueue(href=image_href, referrer=doc_href)
        item.save()

    def update(self):
        if GifQueue.objects.count() < 1:
            logging.info('Queue empty')
            return

        item = GifQueue.objects.all()[0]

        logging.info('Fetching %s...' % (item.href))
        try:
            remote = urllib2.urlopen(item.href, None, 10)
        except urllib2.URLError:
            logging.error('Skipping (Invalid URL)')
        else:
            self.add_image(item, remote)
            remote.close()

        # Whatever happens, delete the queue item
        item.delete()

    def add_image(self, item, remote):
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
        gif.href = item.href
        gif.referrer = item.referrer
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

class GifQueue(models.Model):
    href = models.CharField(max_length=1024)
    referrer = models.CharField(max_length=1024)
    objects = GifQueueManager()

