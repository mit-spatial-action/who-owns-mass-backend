from rest_framework import serializers
from rest_framework_gis import serializers as geoserializers
from who_owns.models import Filing


class FilingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    docket_id = serializers.CharField(read_only=True)
    geometry = geoserializers.GeometryField(read_only=True)
