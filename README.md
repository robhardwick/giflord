# giflord
giflord is a GIF aggregation and listing site for use with [Google App Engine](http://code.google.com/appengine/). The [django-nonrel](http://www.allbuttonspressed.com/projects/django-nonrel) framework is used along with [mechanize](http://wwwsearch.sourceforge.net/mechanize/) and [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) for crawling. All dependencies are bundled so the application is ready to deploy straight away!

## Getting Started

1. [Get a Google App Engine account](https://appengine.google.com/)
2. Fetch the latest version of giflord

    `git clone git://github.com/robhardwick/giflord.git`

3. Update any application settings in `giflord/settings.py`
4. Add the location of giflord as an existing application in the Google App Engine Launcher
5. Run your new application
6. Add demo images by visiting `/cron/queue` once and `/cron/update` multiple times
7. When you're ready, deploy your application
8. You'll start seeing images in your deployed application as soon as the cron hooks have run for the first time

## Dependencies

* [django-nonrel](http://www.allbuttonspressed.com/projects/django-nonrel) v1.2.1 (Bundled)
* [mechanize](http://wwwsearch.sourceforge.net/mechanize/) v0.2.5 with GAE compatibilty patch (Bundled)
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) v3.2 (Bundled)

## Licence
    Copyright (c) 2011 Rob Hardwick, http://github.com/robhardwick

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
