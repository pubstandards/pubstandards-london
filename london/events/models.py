import datetime
import inflect
from dateutil.relativedelta import *

from django.db import models

from london.pubs.models import Pub


p = inflect.engine()

class Event(models.Model):
    pub = models.ForeignKey(Pub)
    date = models.DateField()
    starts = models.TimeField(
        default = datetime.time( 18, 0, 0 ),
        blank = True,
        null = True
    )
    ends = models.TimeField(
        default = datetime.time( 23, 30, 00 ),
        blank = True,
        null = True
    )
    title = models.CharField( max_length=256 )
    slug = models.SlugField( max_length=64 )
    description = models.TextField( blank=True, null=True )
    substandards = models.BooleanField( default=False )
    
    def time_until(self):
        now = datetime.datetime.now()
        starts = datetime.datetime.combine(self.date, self.starts)
        ends = datetime.datetime.combine(self.date, self.ends)
        relative = relativedelta(starts, now)
        days = p.no('day', relative.days)
        hours = p.no('hour', relative.days)
        minutes = p.no('minute', relative.days)
        if relative.days:
            return u'In %s, %s and %s' % ( days, hours, minutes )
        else:
            if relative.hours:
                return u'In %s and %s' % ( hours, minutes )
            else:
                if starts < now:
                    if ends < now:
                        return u'Already happened'
                    else:
                        return u'Happening right now'
                else:
                    return u'In %s' % minutes
    
    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('event-detail', kwargs={'slug':self.slug})
    
    def __unicode__(self):
        return self.title
