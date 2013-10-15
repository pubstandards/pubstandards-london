import datetime

from django.db import models

from london.pubs.models import Pub


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
    
    def __unicode__(self):
        return self.title
