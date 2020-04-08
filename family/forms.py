from datetime import datetime

from django import forms

from admin import models

class FamilySettingForm(forms.Form):
    today = datetime.now()
    years_range = range(today.year - 5, today.year + 6)
    appStartDateDjango = forms.DateField(label="App start date (YYYY-MM-DD)", required=True,
                                         widget=forms.SelectDateWidget(years=years_range))
    challengeEndTime = models.HourMinuteField(label="Challenge end time (H:m)")
    isFitnessSyncOnStart = forms.BooleanField(label="Fitness sync on start", required=False)
    isFitnessSyncScheduled = forms.BooleanField(label="Fitness sync scheduled", required=False)
    isRegularReminderSet = forms.BooleanField(label="Regular reminders scheduled", required=False)

    isGroupInfoNeedsRefresh = forms.BooleanField(label="Group info needs refresh", required=False)
    isStoryListNeedsRefresh = forms.BooleanField(label="Stories needs refresh", required=False)
    isChallengeInfoNeedsRefresh = forms.BooleanField(label="Challenge needs refresh", required=False)
    isFirstRunCompleted = forms.BooleanField(label="First run completed", required=False)
    isDemoMode = forms.BooleanField(label="Demo mode", required=False)

    def form_valid(self, form):
        return super().form_valid(form)
