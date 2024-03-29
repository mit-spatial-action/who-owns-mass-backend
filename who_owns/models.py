from django.contrib.gis.db import models as modelsGIS
from django.db import models
from django import forms

COMPANY_TYPES = (
    ("landlord", "Landlord"),
    ("lawfirm", "Law Firm"),
    ("court", "Court"),
    ("unknown", "Unknown"),
)

LL_SUBTYPES = (
    ("university", "University"),
    ("noncorporate", "Non-corporate"),
    ("corporate", "Corporate"),
    ("housing_authority", "Housing Authority"),
)


class Role(models.Model):
    name = models.CharField(blank=False, null=True, max_length=500)


class Person(models.Model):
    name = models.CharField(blank=False, null=True, max_length=500)
    roles = models.ManyToManyField(Role)
    url = models.URLField(blank=True, null=True)


class Address(modelsGIS.Model):
    street = models.CharField(blank=True, null=True, max_length=200)
    state = models.CharField(blank=True, null=True, max_length=50)
    city = models.CharField(blank=True, null=True, max_length=50)
    zip = models.CharField(blank=True, null=True, max_length=20)
    add1 = models.CharField(blank=True, null=True, max_length=100)
    add2 = models.CharField(blank=True, null=True, max_length=100)
    match_type = models.CharField(blank=True, null=True, max_length=50)
    geocoder = models.CharField(blank=True, null=True, max_length=20)
    geometry = modelsGIS.PointField()


class Parcel(models.Model):
    geometry = modelsGIS.PolygonField()
    addresses = models.ManyToManyField(Address)


class MetaCorp(models.Model):
    """
    'Owner' company. Likely arrived at manually. ID is cluster
    """

    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(blank=True, null=True, max_length=500)


class Institution(models.Model):
    name = models.CharField(blank=True, null=True, max_length=500)
    type = forms.MultipleChoiceField(choices=COMPANY_TYPES)
    ll_subtype = forms.MultipleChoiceField(choices=LL_SUBTYPES)
    people = models.ManyToManyField(Person)
    addresses = models.ManyToManyField(Address)
    cluster = models.CharField(blank=True, null=True, max_length=100)
    metacorp = models.ForeignKey(
        MetaCorp, blank=True, null=True, on_delete=models.DO_NOTHING
    )


class DocketMeta(models.Model):
    docket = models.TextField(primary_key=True, db_index=True)

    class Meta:
        db_table = "docketmeta"


class Docket(models.Model):
    date = models.DateField(blank=True, null=True)
    text = models.CharField(blank=True, null=True, max_length=100)
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
    name = models.CharField(blank=True, null=True, max_length=500)
    address = models.CharField(blank=True, null=True, max_length=200)
    phone = models.CharField(blank=True, null=True, max_length=50)
    add1 = models.CharField(blank=True, null=True, max_length=100)
    add2 = models.CharField(blank=True, null=True, max_length=100)
    city = models.CharField(blank=True, null=True, max_length=50)
    state = models.CharField(blank=True, null=True, max_length=50)
    zip = models.CharField(blank=True, null=True, max_length=20)
    office = models.CharField(blank=True, null=True, max_length=150)
    add_p = models.CharField(blank=True, null=True, max_length=500)
    match_type = models.CharField(blank=True, null=True, max_length=50)
    geocoder = models.CharField(blank=True, null=True, max_length=20)
    geometry = modelsGIS.PointField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "attorneys"

    def __str__(self):
        return self.bar


class Defendant(models.Model):
    name = models.CharField(blank=True, null=True, max_length=500)
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
    name = models.CharField(blank=True, null=True, max_length=500)
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
    session = models.CharField(blank=True, null=True, max_length=70)
    locality = models.CharField(blank=True, null=True, max_length=100)
    location = models.CharField(blank=True, null=True, max_length=50)
    type = models.CharField(blank=True, null=True, max_length=20)
    result = models.CharField(blank=True, null=True, max_length=20)
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
    street = models.CharField(blank=True, null=True, max_length=200)
    state = models.CharField(blank=True, null=True, max_length=50)
    city = models.CharField(blank=True, null=True, max_length=50)
    zip = models.CharField(blank=True, null=True, max_length=20)
    case_type = models.CharField(blank=True, null=True, max_length=50)
    file_date = models.DateField(blank=True, null=True)
    case_status = models.CharField(blank=True, null=True, max_length=20)
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
    add1 = models.CharField(blank=True, null=True, max_length=100)
    add2 = models.CharField(blank=True, null=True, max_length=100)
    add_p = models.TextField(blank=True, null=True)
    match_type = models.CharField(blank=True, null=True, max_length=50)
    geocoder = models.CharField(blank=True, null=True, max_length=20)
    geometry = modelsGIS.PointField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "filings"

    def save(self, *args, **kwargs):
        self.last_updated = self.last_updated.replace(tzinfo=None)
        super(Filing, self).save(*args, **kwargs)


class Judgment(models.Model):
    date = models.DateField(blank=True, null=True)
    type = models.CharField(blank=True, null=True, max_length=50)
    method = models.TextField(blank=True, null=True, max_length=50)
    for_field = models.CharField(
        db_column="for", blank=True, null=True, max_length=200
    )  # Field renamed because it was a Python reserved word.
    against = models.CharField(blank=True, null=True, max_length=200)
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
