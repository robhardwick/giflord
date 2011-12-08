#!/usr/bin/env python
import os
import random
import os
import logging

from google.appengine.ext import blobstore
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

from model import gif_gif
import settings

class GiflordQueue(webapp.RequestHandler):
    def get(self):
        gif_gif.objects.queue()
        self.response.out.write('Successfully Queued')

class GiflordCrawl(webapp.RequestHandler):
    def post(self):
        gif_gif.objects.crawl(self.request.get('url'))
        self.response.out.write('Success')

class GiflordFetch(webapp.RequestHandler):
    def post(self):
        gif_gif.objects.fetch(self.request.get('url'), self.request.get('referrer'))
        self.response.out.write('Success')

class GiflordImage(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, id):
        key = 'gif:'+id
        gif = memcache.get(key)
        if gif is not None:
            self.response.headers['Content-Type'] = 'image/gif'
            self.response.out.write(gif)
            return
        gif = gif_gif.get_by_id(int(id))
        if gif is None:
            self.error(404)
            return
        gif.objects.updateV2(gif)
        if not blobstore.get(gif.image):
            self.error(404)
        else:
            image = blobstore.BlobInfo.get(gif.image)
            if image.size < 1038576:
                # Cache for 1 day
                memcache.set(key, blobstore.fetch_data(image, 0, image.size), 86400)
                logging.info('Cached %s' % (key,))
            self.send_blob(gif.image)

class GiflordBaseHandler(webapp.RequestHandler):
    """Base RequestHandler with some convenience functions."""

    def template_path(self, filename):
        """Returns the full path for a template from its path relative to here."""
        return os.path.join(os.path.dirname(__file__), 'templates', filename)

    def render(self, filename, template_args):
        """Renders a Django template and sends it to the client.
           Args:
           filename: template path (relative to this file)
           template_args: argument dict for the template"""
        template_args.setdefault('uri', self.request.uri)
        template_args.setdefault('dev', os.environ.get('SERVER_SOFTWARE','').startswith('Development'))
        template_args.setdefault('prefix', settings.STATIC_PREFIX)
        template_args.setdefault('subtitle', random.choice(settings.SUBTITLES))
        return template.render(self.template_path(filename), template_args)

class GiflordList(GiflordBaseHandler):
    """Handler for listing gifs"""

    def get_nav(self, test, pos):
        """ Get pagination nav URL"""
        return None if test else '/%d' % (pos,)

    def get(self, num=1):
        """Lists all available albums."""
        key = 'page:'+str(num)
        page = memcache.get(key)
        if page is not None:
            self.response.out.write(page)
            return
        start = (int(num)-1) * settings.RPP
        gifs = gif_gif.all().order('-created').fetch(settings.RPP, start)
        count = len(gifs)
        page = self.render('index.html', {
            'gifs': gifs,
            'count': count,
            'prev': self.get_nav(start < 1, start - 1),
            'next': self.get_nav(count != settings.RPP, start + 1),
        })
        # Cache for 10 minutes
        memcache.set(key, page, 600)
        self.response.out.write(page)
        logging.info('Cached %s' % (key,))

application = webapp.WSGIApplication([
    ('/', GiflordList),
    ('/(\d+)', GiflordList),
    ('/image/(\d+)\.gif', GiflordImage),
    ('/cron/queue', GiflordQueue),
    ('/task/crawl', GiflordCrawl),
    ('/task/fetch', GiflordFetch)],
    debug=True)
 
def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
