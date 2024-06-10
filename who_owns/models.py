from django.contrib.gis.db import models as modelsGIS
from django.db import models
from django import forms


class CompanyType(models.Model):
    """
    Landlord, Court, Law office, etc
    """

    name = models.CharField(blank=False, null=True, unique=True, max_length=300)


class LandlordType(models.Model):
    """
    Corporate, Non-profit, University, etc
    """

    name = models.CharField(blank=False, null=True, unique=True, max_length=300)


class EvictorType(models.Model):
    name = models.CharField(blank=False, null=True, unique=True, max_length=300)


class Role(models.Model):
    name = models.CharField(blank=False, null=True, unique=True, max_length=500)


class Person(models.Model):
    name = models.CharField(blank=False, null=True, max_length=500)
    roles = models.ManyToManyField(Role)
    url = models.URLField(blank=True, null=True)


class Judge(models.Model):
    name = models.CharField(max_length=500, unique=True)
    person = models.ForeignKey(Person, null=True, on_delete=models.DO_NOTHING)

    def save(self, *args, **kwargs):
        # create person instance if judge has not been created yet
        if not self.pk:
            judge_role, _ = Role.objects.get_or_create(name="judge")
            person_instance = Person.objects.create(name=self.name)
            person_instance.roles.add(judge_role)
            self.person = person_instance
        super().save(*args, **kwargs)


class Parcel(models.Model):
    id = models.CharField(primary_key=True, db_index=True, max_length=100)
    geometry = modelsGIS.PolygonField(blank=True, null=True)


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
    parcel = models.ForeignKey(Parcel, null=True, on_delete=models.DO_NOTHING)


class MetaCorp(models.Model):
    """
    'Owner' company. Likely arrived at manually. ID is cluster
    """

    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(blank=True, null=True, max_length=500)
    evictor_type = models.ForeignKey(
        EvictorType, null=True, on_delete=models.DO_NOTHING
    )


class Institution(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(blank=True, null=True, max_length=500)
    landlord_type = models.ForeignKey(
        LandlordType, null=True, on_delete=models.DO_NOTHING
    )
    company_type = models.ForeignKey(
        CompanyType, null=True, on_delete=models.DO_NOTHING
    )
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

    def save(self, *args, **kwargs):
        # create person & role instance if attorney has not been created yet
        if not self.person:
            attorney_role, _ = Role.objects.get_or_create(name="attorney")
            person_instance = Person.objects.create(name=self.name)
            person_instance.roles.add(attorney_role)
            self.person = person_instance
        super().save(*args, **kwargs)

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
    person = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.DO_NOTHING
    )
    institution = models.ForeignKey(
        Institution, null=True, blank=True, on_delete=models.DO_NOTHING
    )
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
    address = models.ForeignKey(
        Address, blank=True, null=True, on_delete=models.DO_NOTHING
    )
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
        if not self.address:
            self.address = Address.objects.create(
                add1=self.add1,
                add2=self.add2,
                street=self.street,
                state=self.state,
                city=self.city,
                zip=self.zip,
                geometry=self.geometry,
                geocoder=self.geocoder,
                match_type=self.match_type,
            )
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
    damage = models.FloatField(null=True, blank=True)
    filing_fees = models.FloatField(null=True, blank=True)
    court_costs = models.FloatField(null=True, blank=True)
    punitive = models.FloatField(null=True, blank=True)
    atty_fee = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    presiding = models.ForeignKey(Judge, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = "judgments"
        unique_together = (
            ("docket", "date", "type", "method", "for_field", "against"),
        )
