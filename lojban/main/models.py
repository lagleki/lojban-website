
import re

from django.db import models
from django.utils import dateformat

friendly_sumti_regexp = re.compile(r'\$?([a-z]+)_\{*(\d)\}*\$?')

class NewsItem(models.Model):
    title = models.CharField(max_length=50, blank=True)
    pub_date = models.DateTimeField("Date published")
    text = models.TextField()

    class Meta:
        ordering = ("-pub_date",)

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return dateformat.format(self.pub_date, "l d F Y")

    class Admin:
        pass

class Gismu(models.Model):
    name = models.CharField(max_length=5)
    cvc_rafsi = models.CharField("CVC rafsi", max_length=3, blank=True)
    ccv_rafsi = models.CharField("CCV rafsi", max_length=3, blank=True)
    cvv_rafsi = models.CharField("CVV rafsi", max_length=4, blank=True)
    english_keyword = models.CharField("English keyword", max_length=20, blank=True)
    hint = models.CharField(max_length=21, blank=True)
    definition = models.TextField()
    notes = models.TextField(blank=True)
    official = models.BooleanField(default=True)

    def _friendly_definition(self):
        return friendly_sumti_regexp.sub(r'\1\2', self.definition)
    _friendly_definition.short_description = "Definition"
    friendly_definition = property(_friendly_definition)

    def _friendly_notes(self):
        return friendly_sumti_regexp.sub(r'\1\2', self.notes)
    _friendly_notes.short_description = "Notes"
    friendly_notes = property(_friendly_notes)

    class Meta:
        verbose_name_plural = "gismu"
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    class Admin:
        list_display = ("name", "cvc_rafsi", "ccv_rafsi", "cvv_rafsi", "english_keyword", "hint", "_friendly_definition")
        search_fields = ("name", "cvc_rafsi", "ccv_rafsi", "cvv_rafsi", "english_keyword", "hint", "definition", "notes")

class WordOfTheDay(models.Model):
    gismu = models.ForeignKey(Gismu)
    pub_date = models.DateField("Date published", auto_now_add=True)
    example_jbo = models.CharField("Lojban example", max_length=200, blank=True)
    example_en = models.CharField("English example", max_length=200, blank=True)
    status = models.IntegerField(choices=[(0, "Unapproved"), (1, "Approved")])
    credits = models.TextField()

    class Meta:
        ordering = ("-pub_date",)

    def __unicode__(self):
        return self.gismu.name

    class Admin:
        list_display = ("gismu", "pub_date")
        search_fields = ["example_en"]
        date_hierarchy = "pub_date"













