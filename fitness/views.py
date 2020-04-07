from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from admin import nav, constants
from fitness import firebase, sync


# Create your views here.
def get_all_families(request):
    template = loader.get_template('view_all_family_fitness.html')
    context = {
        'title': "Family Fitness",
        'nav': nav.get_nav(active=constants.FITNESS),
        'all_families': firebase.get_all_families_shallow(),
    }
    return HttpResponse(template.render(context, request))


def get_family_daily_fitness(request, family_id):
    template = loader.get_template('view_family_fitness.html')
    context = {
        'title': "Family Fitness Data: " + family_id,
        'actions': [
            {
                "uri": "../sync/" + family_id,
                "title": "Sync fitness data",
                "mdc_icon": "sync"
            }
        ],
        'parent_uri': "/fitness/all",
        'data': firebase.get_family_fitness_by_family_id(family_id, 60)
    }
    return HttpResponse(template.render(context, request))


def do_request_fitness_sync(request, family_id):
    if sync.request(family_id):
        messages.add_message(request, messages.INFO, "Fitness sync request for " + family_id + " is completed.")
    else:
        messages.add_message(request, messages.ERROR, "Error when requesting fitness sync for " + family_id + ".")

    return redirect('../daily/' + family_id)
