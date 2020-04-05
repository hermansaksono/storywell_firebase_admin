from django.http import HttpResponse
from django.template import loader

from fitness import firebase


# Create your views here.
def get_all_families(request):
    template = loader.get_template('view_all_family_fitness.html')
    context = {
        'title': "Family Fitness",
        'all_families': firebase.get_all_families_shallow(),
    }
    return HttpResponse(template.render(context, request))


def get_family_daily_fitness(request, family_id):
    template = loader.get_template('view_family_fitness.html')
    context = {
        'title': "Family Fitness Data: " + family_id,
        'parent_uri': "/fitness/all",
        'data': firebase.get_family_fitness_by_family_id(family_id, 60)
    }
    return HttpResponse(template.render(context, request))
