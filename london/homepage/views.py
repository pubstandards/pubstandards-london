import datetime

from django.views.generic import TemplateView

from london.events.models import Event

class HomepageView(TemplateView):
    template_name = 'homepage.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        context['next_events'] = Event.objects.filter(
                date__gte = datetime.date.today()
            ).order_by(
                'date'
            )[:5]
        return context