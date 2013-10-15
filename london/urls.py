from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
import london.events.views
import london.homepage.views
import london.pubs.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'london.views.home', name='home'),
    # url(r'^london/', include('london.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(
        r'^$',
            london.homepage.views.HomepageView.as_view(),
            name='homepage',
    ),
    url(
        r'^event/(?P<slug>.*)$',
            london.events.views.EventDetailView.as_view(),
            name='event-detail',
    ),
    url(
        r'^pub/(?P<slug>.*)$',
            london.pubs.views.PubDetailView.as_view(),
            name='pub-detail',
    ),
    
    url(
        r'^next$',
            london.events.views.NextEvents.as_view(),
            name='next',
    ),
    url(
        r'^next.json$',
            london.events.views.NextEventJSON.as_view(),
            name='next',
    ),
    url(
        r'^next.ics$',
            london.events.views.NextEventsICalFeed(),
            name='nextics',
    ),

    url(
        r'^previously$',
            london.events.views.PreviousEvents.as_view(),
            name='previously',
    ),
    
    url(
        r'^all$',
            london.events.views.AllEvents.as_view(),
            name='all',
    ),
    url(
        r'^all.ics$',
            london.events.views.AllEventsICalFeed(),
            name='allics',
    ),
)
