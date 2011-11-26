from django.conf.urls.defaults import *

urlpatterns = patterns('gif.views',
    # Front end
    ('^$', 'list'),

    # GIFs
    ('^image/(?P<id>\d+)\.gif$', 'image'),

    # Cron
    ('^cron/queue$', 'queue'),

    # Tasks
    ('^task/crawl$', 'crawl'),
    ('^task/fetch$', 'fetch'),
)
