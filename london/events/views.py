import datetime

from django.views.generic import DetailView, ListView

from london.events.models import Event


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'


class NextEvents(ListView):
    model = Event
    template_name = 'next.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        return Event.objects.filter(
                    date__gte = datetime.date.today()
                ).order_by(
                    'date'
                )
