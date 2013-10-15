from django.views.generic import DetailView

from london.pubs.models import Pub


class PubDetailView(DetailView):
    model = Pub
    context_object_name = 'pub'
