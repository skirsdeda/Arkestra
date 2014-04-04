# register all interesting models for search
from django.utils.translation import ugettext_lazy as _

from news_and_events import models, admin
from links import schema, LinkWrapper

schema.register(models.NewsArticle, search_fields=admin.NewsArticleAdmin.search_fields,
    metadata='summary', heading='"Related news"',
    short_text = 'short_title', description='summary',
    )
schema.register(models.Event, search_fields=admin.EventAdmin.search_fields, 
    metadata='summary', heading='"Related events"',
    short_text = 'short_title', description='summary',
    )
