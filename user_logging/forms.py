from datetime import datetime, timedelta
from django import forms


class LogRangeForm(forms.Form):
    start_datetime = datetime.now()
    end_datetime = start_datetime - timedelta(days=30)
    years_range = range(2018, start_datetime.year + 6)
    start_date = forms.DateField(
        label="Start date", initial=start_datetime, widget=forms.SelectDateWidget(years=years_range))
    end_date = forms.DateField(label="End date", initial=end_datetime, widget=forms.SelectDateWidget(years=years_range))

    class Meta:
        fields = ["start_date", "end_date"]

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.send_email()
        return super().form_valid(form)


class RefreshLogForm(forms.Form):
    now = datetime.now()
    years_range = range(2018, now.year + 6)
    end_date = forms.DateField(label="End date", initial=now, widget=forms.SelectDateWidget(years=years_range))

    class Meta:
        fields = ["end_date"]

    def form_valid(self, form):
        return super().form_valid(form)
