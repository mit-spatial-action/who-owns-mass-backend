from django.db import models
from django import forms

COMPANY_TYPES = (
    ("landlord", "Landlord"),
    ("law_firm", "Law Firm"),
    ("property_management", "Property Management"),
    ("unknown", "Unknown"),
)


class Role(models.Model):
    name = models.CharField(blank=False, null=True, max_length=500)


class Person(models.Model):
    name = models.CharField(blank=False, null=True, max_length=500)
    roles = models.ManyToManyField(Role)


class Address(models.Model):
    street = models.CharField(blank=True, null=True, max_length=200)
    state = models.CharField(blank=True, null=True, max_length=50)
    city = models.CharField(blank=True, null=True, max_length=50)
    zip = models.CharField(blank=True, null=True, max_length=20)
    add1 = models.CharField(blank=True, null=True, max_length=100)
    add2 = models.CharField(blank=True, null=True, max_length=100)
    match_type = models.TextField(blank=True, null=True)
    geocoder = models.TextField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)  # This field type is a guess.


class Parcel(models.Model):
    pass


class Institution(models.Model):
    name = models.CharField(blank=True, null=True, max_length=500)
    type = forms.MultipleChoiceField(choices=COMPANY_TYPES)
    people = models.ManyToManyField(Person)
    addresses = models.ManyToManyField(Address)


class DocketMeta(models.Model):
    docket = models.TextField(primary_key=True, db_index=True)

    class Meta:
        db_table = "docketmeta"


class Docket(models.Model):
    date = models.DateField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    docket = models.ForeignKey(
        DocketMeta, null=True, on_delete=models.DO_NOTHING, related_name="docket_meta"
    )

    class Meta:
        managed = True
        db_table = "docket"
        unique_together = (("docket", "date", "text"),)

    def __str__(self):
        return str(self.docket.docket) + ": [" + self.docket.docket + "]"


class DocketOrphan(models.Model):
    docket = models.CharField(blank=True, null=True, max_length=500)
    originator_model = models.CharField(blank=True, null=True, max_length=500)

    class Meta:
        db_table = "docketorphans"


class Attorney(models.Model):
    bar = models.CharField(unique=True, blank=True, primary_key=True, max_length=50)
    person = models.ForeignKey(Person, null=True, on_delete=models.DO_NOTHING)
    name = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    add1 = models.TextField(blank=True, null=True)
    add2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    office = models.TextField(blank=True, null=True)
    add_p = models.TextField(blank=True, null=True)
    match_type = models.TextField(blank=True, null=True)
    geocoder = models.TextField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = True
        db_table = "attorneys"

    def __str__(self):
        return self.bar


class Defendant(models.Model):
    name = models.TextField(blank=True, null=True)
    docket = models.ForeignKey(
        DocketMeta,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="defendant_docket",
    )

    class Meta:
        managed = True
        db_table = "defendants"
        unique_together = (("docket", "name"),)

    def __str__(self):
        if self.name:
            return str(self.id) + ": [" + self.name + "]"
        else:
            return str(self.id)


class Plaintiff(models.Model):
    name = models.TextField(blank=True, null=True)
    person = models.ForeignKey(Person, null=True, on_delete=models.DO_NOTHING)
    docket = models.ForeignKey(
        DocketMeta,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="plaintiff_docket",
    )

    class Meta:
        managed = True
        db_table = "plaintiffs"
        unique_together = (("docket", "name"),)

    def __str__(self):
        if self.name:
            return str(self.id) + ": [" + self.name + "]"
        else:
            return str(self.id)


class Event(models.Model):
    date = models.DateField(blank=True, null=True)
    session = models.TextField(blank=True, null=True)
    locality = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    docket = models.ForeignKey(
        DocketMeta, null=True, on_delete=models.DO_NOTHING, related_name="event_docket"
    )

    class Meta:
        managed = True
        db_table = "events"
        unique_together = (
            ("docket", "date", "locality", "location", "result", "session", "type"),
        )

    def __str__(self):
        return str(self.id) + ": [" + self.docket.docket + "]"


class Filing(models.Model):
    street = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    case_type = models.TextField(blank=True, null=True)
    file_date = models.DateField(blank=True, null=True)
    case_status = models.TextField(blank=True, null=True)
    close_date = models.DateField(blank=True, null=True)
    ptf_attorney = models.ForeignKey(
        Attorney,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="filing_plaintiff_attorney",
    )
    def_attorney = models.ForeignKey(
        Attorney,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="filing_defendant_attorney",
    )
    dispo = models.TextField(blank=True, null=True)
    dispo_date = models.DateField(blank=True, null=True)
    docket = models.ForeignKey(
        DocketMeta, null=True, on_delete=models.DO_NOTHING, related_name="filing_docket"
    )
    district = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    add1 = models.TextField(blank=True, null=True)
    add2 = models.TextField(blank=True, null=True)
    add_p = models.TextField(blank=True, null=True)
    match_type = models.TextField(blank=True, null=True)
    geocoder = models.TextField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = True
        db_table = "filings"

    def save(self, *args, **kwargs):
        self.last_updated = self.last_updated.replace(tzinfo=None)
        super(Filing, self).save(*args, **kwargs)


class Judgment(models.Model):
    date = models.DateField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    method = models.TextField(blank=True, null=True)
    for_field = models.TextField(
        db_column="for", blank=True, null=True
    )  # Field renamed because it was a Python reserved word.
    against = models.TextField(blank=True, null=True)
    docket = models.ForeignKey(
        DocketMeta,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="judgment_docket",
    )

    class Meta:
        managed = True
        db_table = "judgments"
        unique_together = (
            ("docket", "date", "type", "method", "for_field", "against"),
        )
