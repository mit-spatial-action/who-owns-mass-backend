from django.db.models import F
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers import serialize
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from who_owns_mass.models import (
    Site,
    MetaCorp,
    Company,
    Municipality,
    Owner,
    Address,
    Role,
    ParcelPoint,
)

class MuniSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Municipality
        geo_field = "geometry"
        fields = ["name"]

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["addr", "muni", "postal", "state"]

class OwnerSerializer(GeoFeatureModelSerializer):
    address = AddressSerializer()
    geometry = GeometrySerializerMethodField()
    class Meta:
        model = Owner
        geo_field = "geometry"
        fields = ["name", "inst", "trust", "trustees", "address"]

    def get_geometry(self, obj):
        return obj.address.parcel.geometry if obj.address and obj.address.parcel else None

class SiteSerializer(GeoFeatureModelSerializer):
    geometry = GeometrySerializerMethodField()
    class Meta:
        model = Site
        geo_field = "geometry"
        fields = ["id", "fy", "ls_date", "ls_price", "bld_area", "res_area", "units", "bld_val", "lnd_val", "luc", "ooc", "muni", "address"]
    
    def get_geometry(self, obj):
        return obj.address.parcel.geometry if obj.address and obj.address.parcel else None

class MetaCorpDetailSerializer(serializers.ModelSerializer):
    sites = serializers.SerializerMethodField()
    aliases = serializers.SerializerMethodField()

    class Meta:
        model = MetaCorp
        fields = "__all__"
    
    def get_sites(self, obj):
        owners = obj.owners.all()
        return SiteSerializer([site for owner in owners for site in owner.site.all()], many=True).data
    
    def get_aliases(self, obj):
        owners = obj.owners.all()
        return list(set([owner.name for owner in owners]))


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["name"]

class CompanySerializer(serializers.Serializer):
    class Meta:
        model = Company
        fields = ["company_type"]

class SiteDetailSerializer(GeoFeatureModelSerializer):
    address = AddressSerializer()
    geometry = GeometrySerializerMethodField()
    owners = serializers.SerializerMethodField()
    metacorp = serializers.SerializerMethodField()

    class Meta:
        model = Site
        geo_field = "geometry"
        fields = "__all__"

    def get_geometry(self, obj):
        return obj.address.parcel.geometry if obj.address and obj.address.parcel else None

    def get_owners(self, obj):
        owners = obj.owners.all()
        return [OwnerSerializer(owner).data for owner in owners]

    def get_metacorp(self, obj):
        owners = obj.owners.all()
        return [MetaCorpDetailSerializer(owner.metacorp).data for owner in owners][0]