from django.contrib.gis.db import models
from django import forms


class CompanyType(models.Model):
    """
    Landlord, Court, Law office, etc
    """
    name = models.CharField(blank=False, null=True, unique=True, max_length=300)

    class Meta:
        db_table = "company_type"
        managed = True


class LandlordType(models.Model):
    """
    Corporate, Non-profit, University, etc
    """

    name = models.CharField(blank=False, null=True, unique=True, max_length=300)

class Parcel(models.Model):
    id = models.CharField(primary_key=True, db_index=True, max_length=100)
    geometry = models.PolygonField(blank=True, null=True, srid=2249)
    
    class Meta:
        db_table = "parcels"
        managed = True    

class Municipality(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=10)
    muni = models.CharField(null=True, unique=True, max_length=250)
    hns = models.BooleanField(null=True)
    mapc = models.BooleanField(null=True)
    geometry = models.MultiPolygonField(blank=True, null=True, srid=2249)
    
    class Meta:
        managed = True
        db_table = "muni"

class ZipCode(models.Model):
    zip = models.CharField(primary_key=True, unique=True, max_length=50)
    state = models.CharField(max_length=10, null=True, blank=True)
    unambig_state = models.CharField(max_length=10, null=True, blank=True)
    muni_unambig_from = models.CharField(max_length=100, null=True, blank=True)
    muni_unambig_to = models.CharField(max_length=100, null=True, blank=True)
    geometry = models.MultiPolygonField(blank=True, null=True, srid=2249)

    class Meta:
        managed = True
        db_table = "zip"



class BlockGroup(models.Model):
    id = models.BigIntegerField(primary_key=True)
    geometry = models.MultiPolygonField(blank=True, null=True, srid=2249)
    
    class Meta:
        managed = True
        db_table = "block_group"


class Tract(models.Model):
    id = models.BigIntegerField(primary_key=True)
    geometry = models.MultiPolygonField(blank=True, null=True, srid=2249)

    class Meta:
        managed = True
        db_table = "tract"


class ParcelPoint(models.Model):
    """
    Each row is a POINT() representation of a parcel in the MassGIS parcels database.
    """
    id = models.CharField(primary_key=True, db_index=True, max_length=100)
    muni = models.ForeignKey(Municipality, null=True, blank=True, on_delete=models.DO_NOTHING)
    block_group = models.ForeignKey(BlockGroup, null=True, blank=True, on_delete=models.DO_NOTHING)
    tract = models.ForeignKey(Tract, null=True, blank=True, on_delete=models.DO_NOTHING)
    geometry = models.PointField(blank=True, null=True, srid=2249)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    class Meta:
        db_table = "parcels_point"
        managed = True    


class Address(models.Model):
    addr = models.CharField(blank=True, null=True, max_length=500, help_text="Complete number, street name, type string, often reconstructed from address ranges, PO Boxes, etc.")    
    start = models.IntegerField(blank=True, null=True, help_text="For ranges, start of address range. For single-number addresses, that single number.")
    end = models.IntegerField(blank=True, null=True, help_text="For ranges, end of address range. For single-number addresses, that single number.")
    body = models.CharField(blank=True, null=True, max_length=500, help_text="Street name and address type.")
    even = models.BooleanField(default=False, help_text="Whether an address is even or odd.") 	
    muni_str = models.CharField(null=True, blank=True, max_length=250)
    muni = models.ForeignKey(Municipality, null=True, on_delete=models.DO_NOTHING) 	
    postal = models.CharField(null=True, blank=True, max_length=50)	
    state = models.CharField(blank=True, null=True, max_length=10) 
    loc = models.ForeignKey(ParcelPoint, null=True, on_delete=models.DO_NOTHING) 	

    class Meta:
        db_table = "address"
        managed = True


class Site(models.Model):
    id = models.IntegerField(primary_key=True)
    fy = models.IntegerField()
    muni = models.ForeignKey(Municipality, null=True, on_delete=models.DO_NOTHING)
    ls_date = models.DateField(null=True)
    ls_price = models.IntegerField(null=True)
    bld_area = models.IntegerField(null=True)
    res_area = models.IntegerField(null=True)
    units = models.IntegerField(null=False)
    bld_val = models.IntegerField()
    lnd_val = models.IntegerField()
    use_code = models.CharField(null=False, max_length=20)
    luc = models.CharField(null=False, max_length=10)
    ooc = models.BooleanField()
    condo = models.BooleanField()
    address = models.ForeignKey(Address, null=True, on_delete=models.DO_NOTHING)
    
    class Meta:
        managed = True 
        db_table = "site"


class EvictorType(models.Model):
    name = models.CharField(blank=False, null=True, unique=True, max_length=300)


class Role(models.Model):
    """
    attorney, landlord, judge, owner
    """
    name = models.CharField(blank=False, null=True, unique=True, max_length=500)
    class Meta:
        managed = True
        db_table = "role"

class Person(models.Model):
    name = models.CharField(blank=False, null=True, max_length=500)
    roles = models.ManyToManyField(Role)
    url = models.URLField(blank=True, null=True)
    inst = models.BooleanField(null=True)
    class Meta:
        managed = True
        db_table = "person"
        

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


class MetaCorp(models.Model):
    """
    'Owner' company. Likely arrived at manually. ID is network cluster
    """
    id = models.CharField(primary_key=True, max_length=100, db_index=True)
    name = models.CharField(blank=True, null=True, max_length=500)
    val = models.IntegerField(blank=True, null=True)
    evictor_type = models.ForeignKey(EvictorType, null=True, on_delete=models.DO_NOTHING)
    prop_count = models.IntegerField(null=True)
    unit_count = models.FloatField(null=True)
    area = models.IntegerField(null=True)
    units_per_prop = models.FloatField(null=True)
    val_per_prop = models.FloatField(null=True)
    val_per_area = models.FloatField(null=True)
    company_count = models.IntegerField(null=True)
    
    class Meta:
        db_table = "metacorps_network"

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
    geometry = models.PointField(blank=True, null=True)

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
    geometry = models.PointField(blank=True, null=True)

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

class Owner(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(blank=True, null=True, max_length=500)
    inst = models.BooleanField(null=True)
    trust = models.BooleanField(null=True)
    trustees = models.BooleanField(null=True)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.DO_NOTHING)
    cosine_group = models.CharField(null=True, blank=True, max_length=250)
    metacorp = models.ForeignKey(MetaCorp, null=True, blank=True, on_delete=models.DO_NOTHING, help_text="network_group in original data")
    site = models.ForeignKey(Site, null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = "owner"


class Company(models.Model):
    """
    Any kind of companies including LLCs, Trusts, etc. 
    TODO: figure out what to do about courts
    """
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(blank=True, null=True, max_length=500)
    landlord_type = models.ForeignKey(LandlordType, null=True, on_delete=models.DO_NOTHING)
    company_type = models.ForeignKey(CompanyType, null=True, on_delete=models.DO_NOTHING)
    person = models.ManyToManyField(Person, related_name="people")
    owner = models.ManyToManyField(Owner, related_name="owners")
    address = models.ForeignKey(Address, null=True, on_delete=models.DO_NOTHING)
    metacorp = models.ForeignKey(
        MetaCorp, blank=True, null=True, on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return str({self.id: self.name})

    class Meta:
        db_table = "company"
        managed = True

class Plaintiff(models.Model):
    name = models.CharField(blank=True, null=True, max_length=500)
    person = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.DO_NOTHING
    )
    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.DO_NOTHING
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
