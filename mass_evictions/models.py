from django.db import models


class Attorneys(models.Model):
    bar = models.TextField(unique=True, blank=True, null=True)
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
        managed = False
        db_table = 'attorneys'


class Defendants(models.Model):
    name = models.TextField(blank=True, null=True)
    docket = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'defendants'
        unique_together = (('docket', 'name'),)


class Docket(models.Model):
    date = models.DateField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    docket = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'docket'
        unique_together = (('docket', 'date', 'text'),)


class Events(models.Model):
    date = models.DateField(blank=True, null=True)
    session = models.TextField(blank=True, null=True)
    locality = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    docket = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'events'
        unique_together = (('docket', 'date', 'locality', 'location', 'result', 'session', 'type'),)


class Filings(models.Model):
    street = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    case_type = models.TextField(blank=True, null=True)
    file_date = models.DateField(blank=True, null=True)
    case_status = models.TextField(blank=True, null=True)
    close_date = models.DateField(blank=True, null=True)
    ptf_bar = models.TextField(blank=True, null=True)
    def_bar = models.TextField(blank=True, null=True)
    dispo = models.TextField(blank=True, null=True)
    dispo_date = models.DateField(blank=True, null=True)
    docket = models.TextField(unique=True, blank=True, null=True)
    district = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    add1 = models.TextField(blank=True, null=True)
    add2 = models.TextField(blank=True, null=True)
    add_p = models.TextField(blank=True, null=True)
    match_type = models.TextField(blank=True, null=True)
    geocoder = models.TextField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'filings'


class FilingsToMetadata(models.Model):
    filing_id = models.TextField(blank=True, null=True)
    filing = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'filings_to_metadata'
        unique_together = (('filing_id', 'filing'),)


class Judgments(models.Model):
    date = models.DateField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    method = models.TextField(blank=True, null=True)
    for_field = models.TextField(db_column='for', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    against = models.TextField(blank=True, null=True)
    docket = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'judgments'
        unique_together = (('docket', 'date', 'type', 'method', 'for_field', 'against'),)


class Metadata(models.Model):
    id = models.TextField(unique=True, blank=True, null=False, primary_key=True)
    time = models.DateTimeField(blank=True, null=True)
    ip = models.TextField(blank=True, null=True)
    user = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metadata'


class Plaintiffs(models.Model):
    name = models.TextField(blank=True, null=True)
    docket = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plaintiffs'
        unique_together = (('docket', 'name'),)


class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True, null=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True, null=True)
    proj4text = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'
