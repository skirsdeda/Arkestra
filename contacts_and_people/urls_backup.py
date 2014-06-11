from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    'contacts_and_people.views',

    # news, events, vacancies, studentships
    (r'^', include('news_and_events.urls')),
    (r'^', include('vacancies_and_studentships.urls')),

    # housekeeping
    (r'^', include('housekeeping.urls')),
    (r'^', include('arkestra_image_plugin.urls')),
)
