from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    'contacts_and_people.views',

    # person
    url(r"^person/(?P<slug>[-\w]+)/$",
        view="person",
        name="contact-person"
        ),
    url(r"^person/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/$",
        view="person",
        name="contact-person-tab"
        ),

    # place
    url(r"^place/(?P<slug>[-\w]+)/$",
        view="place",
        name="contact-place"
        ),
    url(r"^place/(?P<slug>[-\w]+)/(?P<active_tab>[-\w]*)/$",
        view="place",
        name="contact-place-tab"
        ),

    # lists of people in an entity
    url(
        r"^people/(?P<slug>[-\w]+)/$",
        view="people",
        name="contact-people"
        ),
    url(
        r"^people/(?P<slug>[-\w]+)/(?P<letter>\w)/$",
        view="people",
        name="contact-people-letter"
        ),
    # common people search
    url(
        r"^$",
        view="people_search",
        name="contact-people-search"
        ),

    # main contacts & people page
    url(
        r"^contact/(?:(?P<slug>[-\w]+)/)?$",
        view="contacts_and_people",
        name="contact-entity"
        ),

    #ajax
    url(r"^ajax_people_search/$",
        view="ajax_people_search"),
)
