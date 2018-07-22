from django.template import RequestContext, loader
import json
import time

from atari_manager import glo_atari, glo_romdir, list_cartridges

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
        glo_last_cartridge=filename
        glo_atari.interlock_off()
        time.sleep(0.1)
        glo_atari.load_cartridge(filename) # os.path.join(glo_romdir, filename))
        glo_atari.verify_cartridge(filename) # os.path.join(glo_romdir, filename))
        time.sleep(0.1)
        glo_atari.interlock_on()

    return HttpResponse("okey dokey")

def reset(request):
    glo_atari.reset()

def getStatus(request):
    result = {}

    result["cartridge"] = glo_last_cartridge
    result["cartridges"] = list_cartridges()

    return HttpResponse(json.dumps(result), content_type='application/javascript')
