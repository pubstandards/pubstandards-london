# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'events_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pub', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pubs.Pub'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('starts', self.gf('django.db.models.fields.TimeField')(default=datetime.time(18, 0), null=True, blank=True)),
            ('ends', self.gf('django.db.models.fields.TimeField')(default=datetime.time(23, 30), null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('substandards', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'events', ['Event'])


    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table(u'events_event')


    models = {
        u'events.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ends': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(23, 30)', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pubs.Pub']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '64'}),
            'starts': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(18, 0)', 'null': 'True', 'blank': 'True'}),
            'substandards': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
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

    complete_apps = ['events']