from django.template import RequestContext, loader
import json

from atari_manager import glo_atari, glo_romdir, glo_last_cartridge, list_cartridges

# Create your views here.

from django.http import HttpResponse

glo_last_cartridge = "unknwon"

def index(request):
    template = loader.get_template('atari_web_ui/index.html')
    context = RequestContext(request, {});
    return HttpResponse(template.render(context))

def loadCartridge(request):
    filename = request.GET.get("filename", None)

    if filename:
        glo_last_cartridge=filename
        glo_atari.interlock_off()
        glo_atari.load_cartridge(os.path.join(glo_romdir, filename))
        glo_atari.verify_cartridge(os.path.join(glo_romdir, filename))
        glo_atari.interlock_on()

    return HttpResponse("okey dokey")

def reset(request):
    glo_atari.reset()

def getStatus(request):
    result = {}

    result["cardridge"] = glo_last_cartridge
    result["cartridges"] = list_cartridges()

    return HttpResponse(json.dumps(result), content_type='application/javascript')
