from django.conf.urls.defaults import *

urlpatterns = patterns('gif.views',
    # Front end
    ('^$', 'list'),

    # GIFs
    ('^image/(?P<id>\d+)\.gif$', 'image'),

    # Cron Tasks
    ('^cron/queue$', 'queue'),
    ('^cron/update$', 'update'),
)
