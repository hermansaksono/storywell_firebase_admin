from datetime import datetime
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views import View

from admin import nav, constants
from family.forms import FamilySettingForm
from firebase import firebase_utils
from family import firebase

# Create your views here.
def get_all_families(request):
    template = loader.get_template('view_all_families.html')
    context = {
        'title': "Families",
        'nav': nav.get_nav(active=constants.FAMILY),
        'all_families': firebase.get_all_families_shallow(),
    }
    return HttpResponse(template.render(context, request))


class FamilyUpdateSetting(View):
    def get(self, request, family_id):
        family_setting = None
        if request.user.is_authenticated:
            family_setting = firebase.get_family_by_id(family_id)

        family_setting_form = FamilySettingForm(initial=family_setting)
        # meta_form = GeostoryMetaForm(initial=initial["meta"])
        context = {
            'title': "Edit Family: " + family_id,
            'parent_uri': "/family/all",
            'family_setting': family_setting,
            'family_setting_form': family_setting_form,
            # 'meta_form': meta_form,
        }
        return render(request, 'edit_family_setting.html', context)


    def post(self, request: WSGIRequest, family_id):
        family_setting_form = FamilySettingForm(request.POST)
        if family_setting_form.is_valid:
            data = request.POST.copy()
            appStartDate: datetime = firebase_utils.get_datetime_from_date_str(data.get("appStartDateDjango"))
            isFitnessSyncOnStart: bool = firebase_utils.get_checkbox_boolean(data.get("isFitnessSyncOnStart"))
            isFitnessSyncScheduled: bool = firebase_utils.get_checkbox_boolean(data.get("isFitnessSyncScheduled"))
            isRegularReminderSet: bool = firebase_utils.get_checkbox_boolean(data.get("isRegularReminderSet"))
            isGroupInfoNeedsRefresh: bool = firebase_utils.get_checkbox_boolean(data.get("isGroupInfoNeedsRefresh"))
            isStoryListNeedsRefresh: bool = firebase_utils.get_checkbox_boolean(data.get("isStoryListNeedsRefresh"))
            isFirstRunCompleted: bool = firebase_utils.get_checkbox_boolean(data.get("isFirstRunCompleted"))
            isDemoMode: bool = firebase_utils.get_checkbox_boolean(data.get("isDemoMode"))
            isChallengeInfoNeedsRefresh: bool = firebase_utils\
                .get_checkbox_boolean(data.get("isChallengeInfoNeedsRefresh"))

            geostory_ref = firebase.get_family_ref_by_id(family_id)  # Database
            geostory_ref.update({
                "appStartDate": datetime.timestamp(appStartDate) * 1000,
                "isFitnessSyncOnStart": isFitnessSyncOnStart,
                "isFitnessSyncScheduled": isFitnessSyncScheduled,
                "isRegularReminderSet": isRegularReminderSet,
                "isGroupInfoNeedsRefresh": isGroupInfoNeedsRefresh,
                "isStoryListNeedsRefresh": isStoryListNeedsRefresh,
                "isChallengeInfoNeedsRefresh": isChallengeInfoNeedsRefresh,
                "isFirstRunCompleted": isFirstRunCompleted,
                "isDemoMode": isDemoMode,
            })

            return redirect('./' + family_id)
        else:
            pass
            # messages.error(request, form.errors)
            # return form with entered data, display messages at the top
        pass


    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.send_email()
        return super().form_valid(form)