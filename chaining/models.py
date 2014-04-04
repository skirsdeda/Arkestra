from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __unicode__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey('Category', verbose_name=_('Category'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Sub-Category')
        verbose_name_plural = _('Sub-Categories')

    def __unicode__(self):
        return self.name


class Product(models.Model):
    name = models.SlugField(max_length=255, verbose_name=_('Name'))
    subcategory = models.ForeignKey(SubCategory, verbose_name=_('Subcategory'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
    
    def __unicode__(self):
        return self.name.title()

