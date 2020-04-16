from datetime import datetime, timedelta
from django import forms
from django.utils import timezone

class LogRangeForm(forms.Form):
    start_datetime = timezone.now() - timedelta(days=30)
    years_range = range(2018, start_datetime.year + 6)
    family = forms.ChoiceField(label="Family", widget=forms.Select)
    start_date = forms.DateField(
        label="Start date", initial=start_datetime, widget=forms.SelectDateWidget(years=years_range))
    end_date = forms.DateField(label="End date", initial=timezone.now, widget=forms.SelectDateWidget(years=years_range))
    is_show_raw = forms.BooleanField(label="Show raw logs", initial=False, required=False)

    class Meta:
        fields = ["family", "start_date", "end_date", "is_show_raw"]

    def form_valid(self, form):
        return super().form_valid(form)

    def set_list_of_families(self, families: list, selected=None):
        choices = [(family, family) for family in families]
        self.fields["family"].choices = choices
        if selected is not None:
            self.fields["family"].initial = selected


class RefreshLogForm(forms.Form):
    now = datetime.now()
    years_range = range(2018, now.year + 6)
    end_date = forms.DateField(label="End date", initial=now, widget=forms.SelectDateWidget(years=years_range))

    class Meta:
        fields = ["end_date"]

    def form_valid(self, form):
        return super().form_valid(form)
