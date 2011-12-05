#!/usr/bin/env python
import os
import random
import os
import logging

from google.appengine.ext import blobstore
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
        gif = gif_gif.get_by_id(int(id))
        if gif is None:
            self.error(404)
            return
        gif.objects.updateV2(gif)
        if not blobstore.get(gif.image):
            self.error(404)
        else:
            self.send_blob(gif.image)

class GiflordBaseHandler(webapp.RequestHandler):
    """Base RequestHandler with some convenience functions."""

    def template_path(self, filename):
        """Returns the full path for a template from its path relative to here."""
        return os.path.join(os.path.dirname(__file__), 'templates', filename)

    def render_to_response(self, filename, template_args):
        """Renders a Django template and sends it to the client.
           Args:
           filename: template path (relative to this file)
           template_args: argument dict for the template"""
        template_args.setdefault('current_uri', self.request.uri)
        template_args.setdefault('prefix', settings.STATIC_PREFIX)
        template_args.setdefault('subtitle', random.choice(settings.SUBTITLES))
        self.response.out.write(
            template.render(self.template_path(filename), template_args)
        )

class GiflordList(GiflordBaseHandler):
    """Handler for listing gifs"""

    def get_nav(self, test, pos):
        """ Get pagination nav URL"""
        return None if test else '/%d' % (pos,)

    def get(self, page=1):
        """Lists all available albums."""
        start = (int(page)-1) * settings.RPP
        gifs = gif_gif.all().fetch(settings.RPP, start)
        count = len(gifs)
        self.render_to_response('index.html', {
            'gifs': gifs,
            'count': count,
            'prev': self.get_nav(start < 1, start - 1),
            'next': self.get_nav(count != settings.RPP, start + 1),
        })

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
