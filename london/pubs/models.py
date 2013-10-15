from django.db import models


class Pub(models.Model):
    name = models.CharField( max_length=256 )
    address = models.CharField( max_length=1024, blank=True, null=True )
    latitude = models.FloatField( blank=True, null=True )
    longitude = models.FloatField( blank=True, null=True )
    slug = models.SlugField( max_length=64 )
    
    def __unicode__(self):
        return self.name
    
    def has_latlong(self):
        if self.latitude is not None and self.longitude is not None:
            return True
        else:
            return False
