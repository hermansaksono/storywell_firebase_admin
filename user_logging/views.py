from datetime import datetime

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View

from admin import nav, constants
from firebase import firebase_utils

from fitness import firebase
from . import forms


def get_all_families(request):
    template = loader.get_template('view_all_family_logs.html')
    context = {
        'title': "Family Logs",
        'nav': nav.get_nav(active=constants.LOGS),
        'end_date': firebase_utils.get_date_str_from_datetime(datetime.now()),
        'all_families': firebase.get_all_families_shallow(),
    }
    return HttpResponse(template.render(context, request))


class SelectDateRangeForLogView(View):
    def get(self, request, family_id):
        date_range_form = forms.LogRangeForm()
        context = {
            'title': "Select a Date Range to View Logs for " + family_id,
            'parent_uri': "../all",
            'date_range_form': date_range_form
        }

        return render(request, 'view_date_range_selector.html', context)

    def post(self, request: WSGIRequest, family_id):
        range_form = forms.LogRangeForm(request.POST)
        if range_form.is_valid():
            start_date = firebase_utils.get_date_str_from_datetime(range_form.cleaned_data.get("start_date"))
            end_date = firebase_utils.get_date_str_from_datetime(range_form.cleaned_data.get("end_date"))
            is_show_raw = range_form.cleaned_data.get("")

            if is_show_raw:
                return redirect('../emotions/' + family_id + "/" + start_date + "/" + end_date)
            else:
                return redirect('../emotions/' + family_id + "/" + start_date + "/" + end_date + "/raw")
        else:
            pass
            # messages.error(request, form.errors)
            # return form with entered data, display messages at the top
        pass


class RefreshLogView(View):
    def get(self, request, family_id):
        refresh_log_form = forms.RefreshLogForm()
        context = {
            'title': "Select the End Date Refresh Logs for " + family_id,
            'parent_uri': "../all",
            'refresh_log_form': refresh_log_form
        }

        return render(request, 'view_refresh_log_filter.html', context)

    def post(self, request: WSGIRequest, family_id):
        refresh_log_form = forms.RefreshLogForm(request.POST)
        if refresh_log_form.is_valid():
            end_date = firebase_utils.get_date_str_from_datetime(refresh_log_form.cleaned_data.get("end_date"))
            return redirect('/eventlog/refresh/' + family_id + "/until/" + end_date)
        else:
            pass
            # messages.error(request, form.errors)
            # return form with entered data, display messages at the top
        pass