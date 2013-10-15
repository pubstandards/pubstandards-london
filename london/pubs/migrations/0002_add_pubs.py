# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from django.template.defaultfilters import slugify

pubs = [
    {
        'name': 'Bricklayers Arms',
        'address': '31 Gresse Street, London, W1T 1QS',
        'latitude': '51.517710',
        'longitude': '-0.133483',
    },
    {
        'name': 'De Hems',
        'address': '11 Macclesfield Street, London, W1D 5BW',
        'latitude': '51.512061',
        'longitude': '-0.131218',
    },
    {
        'name': 'Duke of York',
        'address': '47 Rathbone Street, London, W1T 1NQ',
        'latitude': '51.518714',
        'longitude': '-0.135891',
    },
    
    {
        'name': 'The Gunmakers',
        'address': '13 Eyre Street Hill, Clerkenwell, London, EC1R 5ET',
        'latitude': '51.522555',
        'longitude': '-0.110413',
    }
]


class Migration(DataMigration):
    def forwards(self, orm):
        for pub in pubs:
            try:
                slug = pub['slug']
            except KeyError:
                slug = slugify( pub['name'] )
            
            new = orm.Pub(
                name = pub['name'],
                address = pub['address'],
                longitude = pub['longitude'],
                latitude = pub['latitude'],
                slug = slug,
            )
            new.save()

    def backwards(self, orm):
        for pub in pubs:
            try:
                slug = pub['slug']
            except KeyError:
                slug = slugify( pub['name'] )
            
            orm.Pub.objects.filter( slug=slug ).delete()

    models = {
        u'pubs.pub': {
            'Meta': {'object_name': 'Pub'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['pubs']
    symmetrical = True
