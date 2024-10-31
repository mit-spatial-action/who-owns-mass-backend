from django.db.models import F
from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers
from who_owns.models import (
    MetaCorp,
    Company,
    Person,
    Owner,
    LandlordType,
    CompanyType,
    Address,
    Role,
    ParcelPoint,
)


class FilingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    docket_id = serializers.CharField(read_only=True)
    geometry = geoserializers.GeometryField(read_only=True)


class JudgeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class MetaCorpSerializer(serializers.ModelSerializer):
    """
    Sends back all companies related to a single
    requested metacorp as well as any other metacorp stats
    """

    related = serializers.SerializerMethodField()
    owners = serializers.SerializerMethodField()

    def get_related(self, obj):
        related = obj.company_set.all()
        related = related.annotate(
            longitude=F('address__loc__longitude'),
            latitude=F('address__loc__latitude')
        )
        return {
            "companies_count": related.count(),
            "companies": related.values("id", "name", "longitude", "latitude"),
        }

    def get_owners(self, obj):
        return set(obj.owner_set.all().values_list("name", flat=True))


    class Meta:
        model = MetaCorp
        fields = ["id", "name", "related", "owners", "unit_count", "evictor_type", "area", "units_per_prop", "val_per_prop", "val_per_area"]


class MetaCorpListSerializer(serializers.ModelSerializer):
    """
    Sends back all metacorps including company count
    """

    company_count = serializers.SerializerMethodField()

    def get_company_count(self, obj):
        # if "count" in self.context["request"].query_params:
        return obj.company_set.count()

    class Meta:
        model = MetaCorp
        fields = ["id", "name", "company_count"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["name"]

class ParcelPointSerializer(serializers.ModelSerializer):
    class Meta:
        mordel = ParcelPoint
        fields = ["longitude", "latitude"]

class AddressSerializer(serializers.ModelSerializer):
    geometry = geoserializers.GeometryField(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    def get_latitude(self, obj):
        return obj.loc.latitude

    def get_longitude(self, obj):
        return obj.loc.longitude

    class Meta:
        model = Address
        fields = ["id", "addr", "muni_str", "postal", "state", "geometry", "latitude", "longitude"]


class PersonSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    roles = serializers.SerializerMethodField()

    def get_roles(self, obj):
        return obj.roles.all().values_list("name", flat=True)

    class Meta:
        model = Person
        fields = "__all__"


class LandlordTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandlordType
        fields = ["name"]


class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = ["name"]

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = "__all__"

class CompanySerializer(serializers.Serializer):
    owner = OwnerSerializer
    class Meta:
        model = Company
        fields = "__all__"


class CompanyDetailsSerializer(serializers.ModelSerializer):
    """
    Owner details:
    Input: Owner ID (unique)
    Output: LLC name, Owner name, evictor type, total number of units,
    total number of properties, code violations (if available),
    lawyer names (if available) other names for the LLCs, # LLCs,
    corporate addresses, total evictions by type,
    """
    metacorp = MetaCorpSerializer(read_only=True)
    people = PersonSerializer(many=True, read_only=True)
    owner = OwnerSerializer(many=True, read_only=True)
    name = serializers.CharField(read_only=True)
    landlord_type = LandlordTypeSerializer(read_only=True)
    company_type = CompanyTypeSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    class Meta:
        model = Company
        fields = ["metacorp", "people", "owner", "name", "landlord_type", "company_type", "address"]


class ParcelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)


class CompanyPortfolioSerializer(serializers.ModelSerializer):
    """
    Output: feature collection with parcel IDs,
    addresses, coordinates, number of units and
    evictions (y/n) for each property owned by the owner)
    """

    metacorp = MetaCorpSerializer()
    company_type = CompanyTypeSerializer(read_only=True)
    landlord_type = LandlordTypeSerializer(read_only=True)
    people = PersonSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "landlord_type",
            "company_type",
            "address",
            "metacorp",
            "people",
        ]