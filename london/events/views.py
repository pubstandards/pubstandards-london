import datetime

from django.http import HttpResponse
from django.utils import simplejson as json
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


class NextEventJSON(ListView):
    def get(self, request, *args, **kwargs):
        event = Event.objects.filter(
                    date__gte = datetime.date.today()
                ).order_by(
                    'date'
                )[0]
        
        data = {
            'title': event.title,
            'pub': event.pub.name,
            'date': event.date.isoformat(),
            'starts': event.starts.isoformat(),
            'ends': event.ends.isoformat(),
            'time_until': event.time_until(),
        }
        
        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )
