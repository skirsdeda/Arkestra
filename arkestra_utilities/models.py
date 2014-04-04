from cms.models.fields import PlaceholderField
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class ArkestraUser(User):
    class Meta:
        proxy = True

    def edits(self):
        return LogEntry.objects.filter(user = self).order_by('-id')
        
    def last_10_edits(self):
        last_edit = self.edits()[10]

        return last_edit
        
    def last_edit(self):    
        last_edit = self.edits()[0].action_time
        
        return last_edit

        
class Insert(models.Model):
    insertion_point=models.SlugField(unique=True, max_length=60,
        help_text=_("Matches the parameter passed to the {% insert %} tag in "
        "your templates"), verbose_name=_('Insertion point'))
    content = PlaceholderField('insert', verbose_name=_('Content'))
    description =  models.TextField(max_length=256, null=True, blank=False,
        help_text=_("To help remind you what this is for"), verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Insert')
        verbose_name_plural = _("Inserts")
    
    def __unicode__(self):
        return self.insertion_point
