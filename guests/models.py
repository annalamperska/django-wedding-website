from __future__ import unicode_literals
import datetime

from django.db import models
from django.dispatch import receiver

# these will determine the default formality of correspondence
ALLOWED_TYPES = [
    ('formal', 'formal'),
    ('fun', 'fun'),
    ('dimagi', 'dimagi'),
]

INVITATION_ID_LENGTH = 6



class Party(models.Model):
    """
    A party consists of one or more guests.
    """
    name = models.TextField()
    category = models.CharField(max_length=20, null=True, blank=True)
    save_the_date_sent = models.DateTimeField(null=True, blank=True, default=None)
    save_the_date_opened = models.DateTimeField(null=True, blank=True, default=None)
    invitation_id = models.CharField(null=True, max_length=INVITATION_ID_LENGTH, db_index=True, default=None, unique=True)
    invitation_sent = models.DateTimeField(null=True, blank=True, default=None)
    invitation_opened = models.DateTimeField(null=True, blank=True, default=None)
    rehearsal_dinner = models.BooleanField(default=False)
    is_attending = models.BooleanField(default=None, null=True)
    transportationNeeded = models.BooleanField(default=False)
    friSatAccommodation = models.BooleanField(default=False)
    satSunAccommodation = models.BooleanField(default=False)
    phoneNumber = models.TextField(null=True, blank=True)
    emailAddress = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return 'Party: {}'.format(self.name)

    @classmethod
    def in_default_order(cls):
        return cls.objects.order_by('category', 'name')

    @property
    def ordered_guests(self):
        return self.guest_set.order_by('is_plus_one', 'pk')

    @property
    def any_guests_attending(self):
        return any(self.guest_set.values_list('is_attending', flat=True))


MEALS = [
    ('all', 'brak'),
    ('vege', 'vege'),
    ('vegan', 'vegan'),
]


class Guest(models.Model):
    """
    A single guest
    """
    party = models.ForeignKey('Party', on_delete=models.CASCADE)
    first_name = models.TextField()
    last_name = models.TextField(null=True, blank=True)
    is_attending = models.BooleanField(default=None, null=True)
    meal = models.CharField(max_length=20, choices=MEALS, null=True, blank=True)
    is_allergic = models.BooleanField(default=False, null=True)
    allergic = models.TextField(null=True, blank=True)
    is_plus_one = models.BooleanField(default=False)
    plus_one_name = models.TextField(null=True, blank=True)

    @property
    def name(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    @property
    def unique_id(self):
        # convert to string so it can be used in the "add" templatetag
        return str(self.pk)

    def __str__(self):
        return 'Guest: {} {}'.format(self.first_name, self.last_name)
