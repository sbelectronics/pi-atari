from django.template import RequestContext, loader
import json
import time

from atari_manager import glo_atari_manager

# Create your views here.

from django.http import HttpResponse

glo_last_cartridge = "unknwon"

def index(request):
    template = loader.get_template('atari_web_ui/index.html')
    context = RequestContext(request, {});
    return HttpResponse(template.render(context))

def loadCartridge(request):
    global glo_last_cartridge

    filename = request.GET.get("filename", None)

    if filename:
        glo_atari_manager.load_cartridge(filename)

    return HttpResponse("okey dokey")

def loadDelta(request):
    amount = int(request.GET.get("delta", "0"))
    if amount:
        glo_atari_manager.load_delta(amount)
        return HttpResponse("okey dokey")

    return HttpResponse("nope")

def reset(request):
    glo_atari_manager.reset()

    return HttpResponse("okey dokey")

def getStatus(request):
    result = {}

    result["cartridge"] = glo_atari_manager.last_cartridge
    result["cartridges"] = glo_atari_manager.cartridges
    result["categories"] = glo_atari_manager.categories

    return HttpResponse(json.dumps(result), content_type='application/javascript')
