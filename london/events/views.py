from django.views.generic import DetailView

from london.events.models import Event


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'
