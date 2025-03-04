from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField
)
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer, 
    GeometrySerializerMethodField
)
from who_owns_mass.models import (
    Site,
    MetaCorp,
    Owner,
    Address
)

class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = ["addr", "body", "start", "muni", "postal", "state"]

class OwnerSerializer(GeoFeatureModelSerializer):
    address = AddressSerializer()
    geometry = GeometrySerializerMethodField()
    class Meta:
        model = Owner
        geo_field = "geometry"
        fields = ["name", "inst", "trust", "trustees", "address", "metacorp", "site"]

    def get_geometry(self, obj):
        return obj.address.parcel.geometry if obj.address and obj.address.parcel else None

class SimpleSiteSerializer(GeoFeatureModelSerializer):
    address = AddressSerializer()
    geometry = GeometrySerializerMethodField()
    owners = SerializerMethodField()

    class Meta:
        model = Site
        geo_field = "geometry"
        fields = ["id", "fy", "owners", "ls_date", "ls_price", "bld_area", "res_area", "units", "bld_val", "lnd_val", "luc", "ooc", "muni", "address"]
    
    def get_owners(self, obj):
        owners = obj.owners.all()
        return [OwnerSerializer(owner).data for owner in owners]
    
    def get_geometry(self, obj):
        return obj.address.parcel.geometry if obj.address and obj.address.parcel else None

class MetaCorpSerializer(ModelSerializer):
    sites = SerializerMethodField()
    aliases = SerializerMethodField()

    class Meta:
        model = MetaCorp
        fields = "__all__"
    
    def get_sites(self, obj):
        owners = obj.owners.all()
        return SimpleSiteSerializer([site for owner in owners for site in owner.site.all()], many=True).data
    
    def get_aliases(self, obj):
        owners = obj.owners.all()
        return list(set([owner.name for owner in owners]))

class MetaCorpProps(ModelSerializer):
    class Meta:
        model = MetaCorp
        fields =  "__all__"

class SiteSerializer(GeoFeatureModelSerializer):
    address = AddressSerializer()
    geometry = GeometrySerializerMethodField()
    owners = SerializerMethodField()
    metacorp = SerializerMethodField()

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
        return [MetaCorpProps(owner.metacorp).data for owner in owners][0]