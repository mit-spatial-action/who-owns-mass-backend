from rest_framework import permissions
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from who_owns_mass.models import MetaCorp, Site

from who_owns_mass.serializers import SiteSerializer, MetaCorpSerializer

class SmallResultsSetPagination(LimitOffsetPagination):
    default_limit = 3  # Limit to 5 items per page
    max_limit = 3  # Optional: maximum allowed page size

class SiteViewset(ReadOnlyModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    pagination_class = SmallResultsSetPagination

class MetaCorpViewset(ReadOnlyModelViewSet):
    queryset = MetaCorp.objects.all()
    serializer_class = MetaCorpSerializer
    pagination_class = SmallResultsSetPagination