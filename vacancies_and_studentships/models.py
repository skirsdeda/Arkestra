from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin

from arkestra_utilities.output_libraries.dates import nice_date
from arkestra_utilities.generic_models import ArkestraGenericPluginOptions, ArkestraGenericModel
from arkestra_utilities.mixins import URLModelMixin
from arkestra_utilities.settings import PLUGIN_HEADING_LEVELS, PLUGIN_HEADING_LEVEL_DEFAULT
from arkestra_utilities.output_libraries.dates import nice_date

from contacts_and_people.models import Entity, Person #, default_entity_id


class VacancyStudentshipBase(ArkestraGenericModel, URLModelMixin):
    class Meta:
        abstract = True
        ordering = ['date']

    date = models.DateField(verbose_name=_('Closing date'))

    description = models.TextField(null=True, blank=True,
        help_text=_("No longer used"),
        verbose_name=_('Description'))

    auto_page_view_name = "vacancies-and-studentships"

    @property
    def get_when(self):
        """
        get_when provides a human-readable attribute under which items can be
        grouped. Usually, this is an easily-readble rendering of the date (e.g.
        "April 2010") but it can also be "Top news", for items to be given
        special prominence.
        """
        try:
            # The render function of CMSNewsAndEventsPlugin can set a temporary sticky attribute for Top news items
            if self.sticky:
                return "Top items"
        except AttributeError:
            pass

        date_format = "F Y"
        get_when = nice_date(self.date, date_format)
        return get_when


class Vacancy(VacancyStudentshipBase):
    view_name = "vacancy"

    job_number = models.CharField(max_length=9)
    salary = models.CharField(blank=True, max_length=255, null=True,
        help_text=_("Please include currency symbol"))

    class Meta(VacancyStudentshipBase.Meta):
        verbose_name = _('Vacancy')
        verbose_name_plural = _("vacancies")


class Studentship(VacancyStudentshipBase):
    view_name = "studentship"

    supervisors = models.ManyToManyField(Person, null=True, blank=True,
        related_name="%(class)s_people", 
        verbose_name=_('Supervisors'))

    class Meta:
        verbose_name_plural = "studentships"

class VacanciesPlugin(CMSPlugin, ArkestraGenericPluginOptions):
    DISPLAY = (
        (u"vacancies & studentships", u"Vacancies and studentships"),
        (u"vacancies", u"Vacancies only"),
        (u"studentships", u"Studentships only"),
    )
    display = models.CharField(max_length=25,choices=DISPLAY, default="vacancies & studentships", verbose_name=_('Display'))
    # entity = models.ForeignKey(Entity, null=True, blank=True,
    #     help_text="Leave blank for autoselect", related_name="%(class)s_plugin")
    vacancies_heading_text = models.CharField(max_length=25, verbose_name=_('Vacancies heading text'), default="Vacancies")
    studentships_heading_text = models.CharField(max_length=25, verbose_name=_('Studentship heading text'), default="Studentships")
