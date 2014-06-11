from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class ContactsAndPeopleApphook(CMSApp):
    name = _("Contacts and people apphook")
    urls = ["contacts_and_people.urls"]

apphook_pool.register(ContactsAndPeopleApphook)
