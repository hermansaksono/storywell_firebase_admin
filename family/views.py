from datetime import datetime

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View

from admin import nav, constants
from admin.models import HourMinute
from family.forms import FamilySettingForm
from family import firebase

# Create your views here.
def get_all_families(request):
    template = loader.get_template('view_all_families.html')
    context = {
        'title': "Families",
        'nav': nav.get_nav(active=constants.FAMILY),
        'all_families': firebase.get_families(),
    }
    return HttpResponse(template.render(context, request))


class FamilyUpdateSetting(View):
    def get(self, request, family_id):
        family_setting = None
        if request.user.is_authenticated:
            family_setting = firebase.get_family_by_id(family_id)

        family_setting_form = FamilySettingForm(initial=family_setting)
        context = {
            'title': "Edit Family: " + family_id,
            'parent_uri': "/family/all",
            'fitness_sync_uri': "/fitness/sync/" + family_id,
            'family_setting': family_setting,
            'family_setting_form': family_setting_form,
            # 'meta_form': meta_form,
        }
        return render(request, 'edit_family_setting.html', context)


    def post(self, request: WSGIRequest, family_id):
        family_setting_form = FamilySettingForm(request.POST)
        if family_setting_form.is_valid():
            data = family_setting_form.cleaned_data
            app_start_date: datetime = datetime.combine(data.get("appStartDateDjango"), datetime.min.time())
            aware_app_start_date: datetime = timezone.make_aware(app_start_date)

            challenge_end_time : HourMinute = data.get("challengeEndTime")
            is_fitness_sync_on_start: bool = data.get("isFitnessSyncOnStart")
            is_fitness_sync_scheduled: bool = data.get("isFitnessSyncScheduled")
            is_regular_reminder_set: bool = data.get("isRegularReminderSet")
            is_group_info_needs_refresh: bool = data.get("isGroupInfoNeedsRefresh")
            is_story_list_needs_refresh: bool = data.get("isStoryListNeedsRefresh")
            is_first_run_completed: bool = data.get("isFirstRunCompleted")
            is_demo_mode: bool = data.get("isDemoMode")
            is_challenge_info_needs_refresh: bool = data.get("isChallengeInfoNeedsRefresh")

            family_ref = firebase.get_family_ref_by_id(family_id)
            family_ref.update({
                "appStartDate": datetime.timestamp(aware_app_start_date) * 1000,
                "challengeEndTime": challenge_end_time.to_json(),
                "isFitnessSyncOnStart": is_fitness_sync_on_start,
                "isFitnessSyncScheduled": is_fitness_sync_scheduled,
                "isRegularReminderSet": is_regular_reminder_set,
                "isGroupInfoNeedsRefresh": is_group_info_needs_refresh,
                "isStoryListNeedsRefresh": is_story_list_needs_refresh,
                "isChallengeInfoNeedsRefresh": is_challenge_info_needs_refresh,
                "isFirstRunCompleted": is_first_run_completed,
                "isDemoMode": is_demo_mode,
            })

            return redirect('./' + family_id)
        else:
            messages.error(request, family_setting_form.errors)
            return redirect('./' + family_id)
        pass


    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.send_email()
        return super().form_valid(form)