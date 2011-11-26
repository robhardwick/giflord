import logging
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from gif.models import Gif

def list(request):
    """ Render list of GIFs """
    gifs = Gif.objects.all()
    return render_to_response('list.html', {
        'gifs': gifs,
        'count': len(gifs)
    })

def image(request, id):
    """ Fetch and return a GIF image file"""
    gif = get_object_or_404(Gif, id=id)
    return HttpResponse(gif.image, 'image/gif')

@csrf_exempt
def queue(request):
    Gif.objects.queue()
    return HttpResponse('Success', 'text/plain')

@csrf_exempt
def crawl(request):
    Gif.objects.crawl(request.POST['url'])
    return HttpResponse('Success', 'text/plain')

@csrf_exempt
def fetch(request):
    Gif.objects.fetch(request.POST['url'], request.POST['referrer'])
    return HttpResponse('Success', 'text/plain')
