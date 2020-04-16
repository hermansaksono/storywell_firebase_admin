from datetime import datetime

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View

from admin import nav, constants
from firebase import firebase_utils

from group.models import User
from family import firebase as family_firebase
from user_logging import helpers
from . import forms, firebase


def get_all_families(request):
    template = loader.get_template('view_all_family_logs.html')
    context = {
        'title': "Family Logs",
        'nav': nav.get_nav(active=constants.LOGS),
        'end_date': firebase_utils.get_date_str_from_datetime(datetime.now()),
        'all_families': family_firebase.get_families(),
    }
    return HttpResponse(template.render(context, request))


class SelectDateRangeForLogView(View):
    def get(self, request, family_id):
        today_date: str = firebase_utils.get_date_str_from_datetime(datetime.now())
        date_range_form = forms.LogRangeForm()
        context = {
            'title': "Select a Date Range to View Logs for " + family_id,
            'parent_uri': "../all",
            'action_view_today_log_uri': "../emotions/" + family_id + "/" + today_date + "/" + today_date + "/raw",
            'date_range_form': date_range_form
        }

        return render(request, 'view_date_range_selector.html', context)

    def post(self, request: WSGIRequest, family_id):
        range_form = forms.LogRangeForm(request.POST)
        if range_form.is_valid():
            start_date = firebase_utils.get_date_str_from_datetime(range_form.cleaned_data.get("start_date"))
            end_date = firebase_utils.get_date_str_from_datetime(range_form.cleaned_data.get("end_date"))
            is_show_raw = range_form.cleaned_data.get("is_show_raw")

            if is_show_raw:
                return redirect('../emotions/' + family_id + "/" + start_date + "/" + end_date + "/raw")
            else:
                return redirect('../emotions/' + family_id + "/" + start_date + "/" + end_date)
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


class PrintableLogView(View):
    def get(self, request, user_id: str, start_date_str: str, end_date_str: str, show_data="not_raw"):
        try:
            user: User = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return HttpResponse("User not found")

        is_show_raw: bool = False if show_data is "not_raw" else True
        logs_by_day: dict = firebase.get_logs_by_day(user, start_date_str, end_date_str, is_show_raw)

        template = loader.get_template('view_minute_logs.html')
        context = {
            'user_id': user_id,
            'start_date': helpers.get_friendly_date_from_str(start_date_str),
            'end_date': helpers.get_friendly_date_from_str(end_date_str),
            'log_data': logs_by_day,
            'is_show_raw': is_show_raw
        }

        return HttpResponse(template.render(context, request))