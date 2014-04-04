import datetime, json
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.core import serializers
from arkestra_utilities.views import ArkestraGenericView

from contacts_and_people.models import Entity

from models import Event, NewsArticle
from .lister import NewsAndEventsCurrentLister, NewsArchiveLister, \
    EventsArchiveLister, EventsForthcomingLister


from arkestra_utilities.settings import MULTIPLE_ENTITY_MODE

class NewsAndEventsView(ArkestraGenericView):
    auto_page_attribute = "auto_news_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = NewsAndEventsCurrentLister(
            entity=self.entity,
            request=self.request
            )

        self.main_page_body_file = "arkestra/generic_lister.html"
        self.meta = {"description": _("Recent news and forthcoming events"),}
        self.title = unicode(self.entity) + _(" news & events")
        if MULTIPLE_ENTITY_MODE:
            self.pagetitle = unicode(self.entity) + _(" news & events")
        else:
            self.pagetitle = _("News & events")

        return self.response(request)

class NewsArchiveView(ArkestraGenericView):
    auto_page_attribute = "auto_news_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = NewsArchiveLister(
            entity=self.entity,
            request=self.request
            )

        self.main_page_body_file = "arkestra/generic_filter_list.html"
        self.meta = {"description": _("Searchable archive of news items"),}
        self.title = _("News archive for %s") % unicode(self.entity)
        self.pagetitle = _("News archive for %s") % unicode(self.entity)

        return self.response(request)

class EventsArchiveView(ArkestraGenericView):
    auto_page_attribute = "auto_news_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = EventsArchiveLister(
            entity=self.entity,
            request=self.request
            )

        self.main_page_body_file = "arkestra/generic_filter_list.html"
        self.meta = {"description": _("Searchable archive of events"),}
        self.title = _("Events archive for %s") % unicode(self.entity)
        self.pagetitle = _("Events archive for %s") % unicode(self.entity)

        return self.response(request)


class EventsForthcomingView(ArkestraGenericView):
    auto_page_attribute = "auto_news_page"

    def get(self, request, *args, **kwargs):
        self.get_entity()

        self.lister = EventsForthcomingLister(
            entity=self.entity,
            request=self.request
            )

        self.main_page_body_file = "arkestra/generic_filter_list.html"
        self.meta = {"description": _("Searchable list of forthcoming events"),}
        self.title = _("Forthcoming events for %s") % unicode(self.entity)
        self.pagetitle = _("Forthcoming events for %s") % unicode(self.entity)

        return self.response(request)


def newsarticle(request, slug):
    """
    Responsible for publishing news article
    """
    if request.user.is_staff:
        newsarticle = get_object_or_404(NewsArticle, slug=slug)
    else:
        newsarticle = get_object_or_404(NewsArticle, slug=slug, published=True, date__lte=datetime.datetime.now())
    return render_to_response(
        "news_and_events/newsarticle.html",
        {
        "newsarticle":newsarticle,
        "entity": newsarticle.get_hosted_by,
        "meta": {"description": newsarticle.summary,}
        },
        RequestContext(request),
    )

def event(request, slug):
    """
    Responsible for publishing an event
    """
    # print " -------- views.event --------"
    event = get_object_or_404(Event, slug=slug)

    return render_to_response(
        "news_and_events/event.html",
        {"event": event,
        "entity": event.get_hosted_by,
        "meta": {"description": event.summary,},
        },
        RequestContext(request),
        )
