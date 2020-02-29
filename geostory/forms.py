from django import forms


class GeostoryMetaForm(forms.Form):
    isShowAverageSteps = forms.BooleanField(label="Show average steps", required=False)
    isShowNeighborhood = forms.BooleanField(label="Show neighborhood", required=False)
    transcript = forms.CharField(widget=forms.Textarea, required=False)

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.send_email()
        return super().form_valid(form)


class GeostoryForm(forms.Form):
    isReviewed = forms.BooleanField(label="Is reviewed", required=False)

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.send_email()
        return super().form_valid(form)