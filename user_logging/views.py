from datetime import datetime
from django.http import HttpResponse
from django.template import loader
from firebase import firebase_utils

from fitness import firebase

def get_all_families(request):
    template = loader.get_template('view_all_family_logs.html')
    context = {
        'title': "Family Logs",
        'end_date': firebase_utils.get_date_str_from_datetime(datetime.now()),
        'all_families': firebase.get_all_families_shallow(),
    }
    return HttpResponse(template.render(context, request))


def select_date_range_for_logs(request, family_id):
    template = loader.get_template('view_date_range_selector.html')
    context = {
        'title': "Select Date Range to View Logs",
        'parent_uri': "../all"
    }

    return HttpResponse(template.render(context, request))