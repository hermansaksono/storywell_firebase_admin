from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views import View

from firebase import firebase_utils
from geostory import firebase
from geostory.forms import GeostoryForm, GeostoryMetaForm


def get_all_geostory(request):
    firebase.get_all_stories()
    template = loader.get_template('geostory/view_all_geostories.html')
    context = {
        'all_geostories': firebase.get_all_stories(),
    }
    return HttpResponse(template.render(context, request))


class GeoStoryUpdateView(View):
    def get(self, request, geostory_id):
        initial = None
        if request.user.is_authenticated:
            initial = firebase.get_geostory_by_id(geostory_id)
        geostory_form = GeostoryForm(initial=initial)
        meta_form = GeostoryMetaForm(initial=initial["meta"])
        context = {
            'geostory_form': geostory_form,
            'meta_form': meta_form,
            'geostory': initial
        }
        return render(request, 'geostory/edit_geostory.html', context)

    def post(self, request: WSGIRequest, geostory_id):
        geostory_form = GeostoryForm(request.POST)
        meta_form = GeostoryMetaForm(request.POST)
        if geostory_form.is_valid and meta_form.is_valid:
            geostory_data = request.POST.copy()
            is_reviewed: bool = firebase_utils.get_checkbox_boolean(geostory_data.get("isReviewed"))
            is_show_avg_steps: bool = firebase_utils.get_checkbox_boolean(geostory_data.get("isShowAverageSteps"))
            is_show_neighborhood: bool = firebase_utils.get_checkbox_boolean(geostory_data.get("isShowNeighborhood"))

            geostory_ref = firebase.get_geostory_ref_by_id(geostory_id)  # Database
            geostory_ref.update({
                "isReviewed": is_reviewed
            })

            geostory_meta_ref = firebase.get_geostory_meta_ref_by_id(geostory_id)  # Database
            geostory_meta_ref.update({
                "isShowAverageSteps": is_show_avg_steps,
                "isShowNeighborhood": is_show_neighborhood,
                "transcript": geostory_data.get("transcript")
            })
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