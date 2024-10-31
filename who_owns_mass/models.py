from django.contrib.gis.db import models
from django import forms

class MetaCorp(models.Model):
    """
    DONE
    'Owner' company. Likely arrived at manually. ID is network cluster
    """
    id = models.CharField(
        primary_key=True, 
        max_length=100, 
        db_index=True
        )
    name = models.CharField(
        blank=True, 
        null=True, 
        max_length=500,
        help_text="Most common company name within metacorp."
        )
    val = models.IntegerField(
        blank=True, 
        null=True,
        help_text="Summed building and residential value held by a particular metacorp."
        )
    prop_count = models.IntegerField(
        blank=True, 
        null=True,
        help_text="Number of properties (i.e., sites rows) linked to a given metacorp."
        )
    unit_count = models.FloatField(
        blank=True, 
        null=True,
        help_text="Estimated number of units linked to a given metacorp."
        )
    area = models.IntegerField(
        blank=True, 
        null=True,
        help_text="Summed building area held by a particular metacorp (where 'building area' means the larger of res_area and bld_area)."
        )
    units_per_prop = models.FloatField(
        blank=True, 
        null=True,
        help_text="Total estimated units divided by the property count. This is a measure of what scale of property a given owner invests in."
        )
    val_per_prop = models.FloatField(
        blank=True, 
        null=True,
        help_text="Total value divided by property count. A measure of how valuable a given metacorps properties are."
        )
    val_per_area = models.FloatField(
        blank=True, 
        null=True,
        help_text="Value per square foot. Another measure of how valuable a metacorps properties are."
        )
    company_count = models.IntegerField(
        blank=True, 
        null=True,
        help_text="How many unique companies appear within a given metacorp."
        )
    
    class Meta:
        db_table = "metacorps_network"

class Municipality(models.Model):
    """
    DONE
    Massachusetts municipalities.
    """
    id = models.CharField(
        primary_key=True, 
        max_length=250
        )
    muni = models.CharField(
        null=False, 
        unique=False, 
        max_length=250,
        help_text="Name of municipality."
        )
    state = models.CharField(
        null=True, 
        unique=False, 
        max_length=25,
        help_text="Name of municipality."
        )
    hns = models.BooleanField(
        null=False,
        default=False,
        help_text="If TRUE, municipality is one of the Healthy Neighborhoods Study areas."
        )
    mapc = models.BooleanField(
        null=False,
        default=False,
        help_text="If TRUE, municipality is part of the MAPC region."
        )
    geometry = models.MultiPolygonField( 
        blank=False, 
        null=False,
        srid=4326
        )
    
    class Meta:
        managed = True
        db_table = "muni"

class ZipCode(models.Model):
    """
    DONE
    Each row is a ZIP code boundary some of which intersects with Massachusetts. (ZIPS can cross state lines).
    """
    zip = models.CharField(
        primary_key=True,
        max_length=50,
        help_text="Unique identifier (i.e., the 11-digit GEOID)."
        )
    geometry = models.MultiPolygonField(
        blank=False, 
        null=False, 
        srid=4326
        )

    class Meta:
        managed = True
        db_table = "zip"

class BlockGroup(models.Model):
    """
    Each row is a Massachusetts block group from the most recent vintage available in tigris.
    DONE
    """
    id = models.CharField(
        primary_key=True,
        max_length=12,
        help_text="Unique identifier (i.e., the 12-digit GEOID)."
        )
    geometry = models.MultiPolygonField(
        blank=False, 
        null=False, 
        srid=4326
        )
    
    class Meta:
        managed = True
        db_table = "block_group"


class Tract(models.Model):
    """
    Each row is a Massachusetts Tract from the most recent vintage available in tigris.
    DONE
    """
    id = models.CharField(
        primary_key=True,
        max_length=11,
        help_text="Unique identifier (i.e., the 11-digit GEOID)."
        )
    geometry = models.MultiPolygonField(
        blank=False, 
        null=False, 
        srid=4326
        )

    class Meta:
        managed = True
        db_table = "tract"


class ParcelPoint(models.Model):
    """
    DONE
    Each row is a POINT() representation of a parcel in the MassGIS parcels database.
    """
    id = models.CharField(primary_key=True, db_index=True, max_length=100)
    muni = models.ForeignKey(
        Municipality, 
        null=True, 
        blank=True, 
        on_delete=models.DO_NOTHING
        )
    block_group = models.ForeignKey(
        BlockGroup, 
        null=True, 
        blank=True, 
        on_delete=models.DO_NOTHING
        )
    tract = models.ForeignKey(
        Tract, 
        null=True, 
        blank=True, 
        on_delete=models.DO_NOTHING
        )
    lat = models.FloatField(
        null=True
        )
    lng = models.FloatField(
        null=True
        )
    geometry = models.PointField(
        blank=False, 
        null=False, 
        srid=4326
        )

    class Meta:
        db_table = "parcels_point"
        managed = True    


class Address(models.Model):
    """
    DONE
    Each row is a unique address (including parsed ranges) found in any of assessors, sites, owners, companies, or owners. 
    Constructed, in part, using the statewide and Boston address layers as a reference dataset.
    """
    id = models.IntegerField(
        primary_key=True, 
        db_index=True
        )
    addr = models.CharField(
        blank=True, 
        null=True, 
        max_length=500, 
        help_text="Complete number, street name, type string, often reconstructed from address ranges, PO Boxes, etc."
        )    
    start = models.DecimalField(
        blank=True, 
        null=True, 
        decimal_places=1,
        max_digits=100,
        help_text="For ranges, start of address range. For single-number addresses, that single number."
        )
    end = models.DecimalField(
        blank=True, 
        null=True, 
        decimal_places=1,
        max_digits=100,
        help_text="For ranges, end of address range. For single-number addresses, that single number."
        )
    body = models.CharField(
        blank=True, 
        null=True, 
        max_length=500, 
        help_text="Street name and address type."
        )
    even = models.BooleanField(
        default=False, 
        help_text="Whether an address is even or odd."
        )
    muni = models.CharField(
        blank=True, 
        null=True, 
        max_length=100, 
        help_text="Municipality name."
        )
    postal = models.CharField(
        null=True, 
        blank=True, 
        max_length=50,
        help_text="Postal code. For US addresses, a ZIP code."
        )	
    state = models.CharField(
        blank=True, 
        null=True, 
        max_length=100,
        help_text="State (or, for international addresses, a region)."
        ) 
    parcel = models.ForeignKey(
        ParcelPoint, 
        null=True, 
        on_delete=models.DO_NOTHING
        ) 	

    class Meta:
        db_table = "address"
        managed = True

class Site(models.Model):
    """
    Residential properties Each row represents a property in the assessors table.
    """
    id = models.IntegerField(
        primary_key=True
        )
    fy = models.IntegerField(
        help_text="Fiscal year of assessor's database."
    )
    muni = models.ForeignKey(
        Municipality, 
        null=True, 
        on_delete=models.DO_NOTHING,
        )
    ls_date = models.DateField(
        null=True,
        help_text="Last sale date. Unmodified from MassGIS, see their documentation."
        )
    ls_price = models.IntegerField(
        null=True,
        help_text="Last sale price. Unmodified from MassGIS, see their documentation."
        )
    bld_area = models.IntegerField(
        null=True,
        help_text="Building area. Unmodified from MassGIS, see their documentation."
        )
    res_area = models.IntegerField(
        null=True,
        help_text="Residential area. Unmodified from MassGIS, see their documentation."
        )
    units = models.IntegerField(
        null=False,
        help_text="Estimated unit count."
        )
    bld_val = models.IntegerField(
        help_text="Building value. Unmodified from MassGIS, see their documentation."
    )
    lnd_val = models.IntegerField(
        help_text="Land value. Unmodified from MassGIS, see their documentation."
    )
    use_code = models.CharField(
        null=False, 
        max_length=20,
        help_text="Use code. Unmodified from MassGIS, see their documentation."
        )
    luc = models.CharField(
        null=False, 
        max_length=10,
        help_text="Land use code. Assigned based on our modified version of a crosswalk supplied by MAPC."
        )
    ooc = models.BooleanField(
        help_text="Owner occupied. If TRUE, listed owner address matches listed property address."
    )
    condo = models.BooleanField(
        help_text="Condo. If TRUE, there are properties with a condo land use code on the parcel (which leads us to treat the whole thing as a 'condo', i.e., a parcel with multiple associated properties)."
    )
    address = models.ForeignKey(
        Address, 
        null=True, 
        on_delete=models.DO_NOTHING
    )
    
    class Meta:
        managed = True 
        db_table = "site"

class Company(models.Model):
    """
    DONE
    Companies from OpenCorporates matched to at least one row in the assessors 
    table, or present in the networks of those companies.
    """
    # id = models.CharField(primary_key=True, max_length=100)
    id = models.IntegerField(primary_key=True)
    name = models.CharField(
        blank=True, 
        null=True, 
        max_length=500
        )
    company_type = models.CharField(
        blank=True, 
        null=True, 
        max_length=500
        )
    address = models.ForeignKey(
        Address, 
        null=True, 
        on_delete=models.DO_NOTHING
        )
    metacorp = models.ForeignKey(
        MetaCorp, 
        blank=True, 
        null=True, 
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return str({self.id: self.name})

    class Meta:
        db_table = "company"
        managed = True

class Owner(models.Model):
    """
    DONE
    Each row represents either a unique owner name-address pair.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(
        blank=True, 
        null=True, 
        max_length=500,
        help_text="Deduplicated owner name."
        )
    inst = models.BooleanField(
        null=True,
        help_text="Institutional owner. If TRUE, we flagged the owner as institutional using keywords unlikely to be identified with individuals."
        )
    trust = models.BooleanField(
        null=True,
        help_text="Trust. If TRUE, we flagged the owner as a trust using keywords."
        )
    trustees = models.BooleanField(
        null=True,
        help_text="Trustees. If TRUE, we flagged the owner as trustees of a trust using keywords."
        )
    address = models.ForeignKey(
        Address, 
        null=True, 
        blank=True, 
        on_delete=models.DO_NOTHING
        )
    metacorp = models.ForeignKey(
        MetaCorp, 
        null=True, 
        blank=True, 
        on_delete=models.DO_NOTHING,
        related_name='owners'
        )
    company = models.ForeignKey(
        Company, 
        null=True, 
        blank=True, 
        on_delete=models.DO_NOTHING
         )
    site = models.ManyToManyField(
        Site, 
        blank=True, 
        through='SiteToOwner',
        related_name='owners'
        )

    class Meta:
        managed = True
        db_table = "owner"

class SiteToOwner(models.Model):
    """
    Represents the many-to-many relationship between owners and sites. 
    All many-to-many relations are induced by splitting non-institutional 
    owners on instances of the word "and" to identify multiple individual 
    owners of a site.
    """
    site = models.ForeignKey(
        Site, 
        null=False, 
        blank=False, 
        on_delete=models.DO_NOTHING,
        help_text="Identifier of property.",
        related_name="site_from_owner"
        )
    owner = models.ForeignKey(
        Owner, 
        null=False, 
        blank=False, 
        on_delete=models.DO_NOTHING,
        help_text="Identifier of owner.",
        related_name="owner_from_site"
        )

    class Meta:
        managed = True
        db_table = "site_to_owner"

class Role(models.Model):
    """
    Roles of officers in companies.
    DONE
    """
    name = models.CharField(primary_key=True, max_length=500)
    class Meta:
        managed = True
        db_table = "role"

class Officer(models.Model):
    """
    Each row represents a unique name-company relationship.
    DONE
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(
        blank=False,
        null=True, 
        max_length=500,
        help_text="Name of officer."
        )
    inst = models.BooleanField(
        default=False,
        null=False,
        help_text="Institutional officer. If TRUE, we flagged the owner as institutional using keywords unlikely to be identified with individuals."
        )
    roles = models.ManyToManyField(
        Role,
        through="OfficerToRole"
        )
    company = models.ForeignKey(
        Company, 
        null=True, 
        on_delete=models.DO_NOTHING,
        )
    address = models.ForeignKey(
        Address, 
        null=True, 
        on_delete=models.DO_NOTHING
        )
    metacorp = models.ForeignKey(
        MetaCorp, 
        null=True, 
        on_delete=models.DO_NOTHING
        )
    class Meta:
        managed = True
        db_table = "officer"

class OfficerToRole(models.Model):
    """
    Officer-to-role through table.
    DONE
    """
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "officer_to_role"