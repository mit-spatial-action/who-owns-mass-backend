from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers
from who_owns.models import (
    MetaCorp,
    Institution,
    Person,
    LandlordType,
    CompanyType,
    Address,
    Role,
)


class FilingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    docket_id = serializers.CharField(read_only=True)
    geometry = geoserializers.GeometryField(read_only=True)


class JudgeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class InstitutionSerializer(serializers.Serializer):
    class Meta:
        model = Institution
        fields = "__all__"


class MetaCorpSerializer(serializers.ModelSerializer):
    """
    Sends back all institutions related to a single
    requested metacorp as well as any other metacorp stats
    """

    institutions = serializers.SerializerMethodField()

    def get_institutions(self, obj):
        institutions = obj.institution_set.all()
        return {
            "institutions_count": institutions.count(),
            "institutions": institutions.values("id", "name"),
        }

    class Meta:
        model = MetaCorp
        fields = ["id", "name", "institutions"]


class MetaCorpListSerializer(serializers.ModelSerializer):
    """
    Sends back all metacorps including institution count
    """

    institution_count = serializers.SerializerMethodField()

    def get_institution_count(self, obj):
        # if "count" in self.context["request"].query_params:
        return obj.institution_set.count()

    class Meta:
        model = MetaCorp
        fields = ["id", "name", "institution_count"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["name"]


class AddressSerializer(serializers.ModelSerializer):
    geometry = geoserializers.GeometryField(read_only=True)

    class Meta:
        model = Address
        fields = ["street", "state", "city", "zip", "geometry"]


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


class InstitutionDetailsSerializer(serializers.ModelSerializer):
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
    name = serializers.CharField(read_only=True)
    landlord_type = LandlordTypeSerializer(read_only=True)
    company_type = CompanyTypeSerializer(read_only=True)
    addresses = AddressSerializer(read_only=True)

    class Meta:
        model = Institution
        fields = "__all__"


class ParcelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)


class InstitutionPortfolioSerializer(serializers.ModelSerializer):
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
        model = Institution
        fields = [
            "id",
            "name",
            "landlord_type",
            "company_type",
            "addresses",
            "metacorp",
            "people",
        ]
