from django.db.models import Q
from django.http import HttpResponse, Http404

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.renderers import JSONRenderer

from who_owns_mass.models import MetaCorp, Company, Site
from who_owns_mass.serializers import (
    SiteDetailSerializer,
    MetaCorpDetailSerializer,
)

class SiteDetail(generics.RetrieveAPIView):
    serializer_class = SiteDetailSerializer

    def get_object(self):
        try:
            return Site.objects.prefetch_related('owners').get(pk=self.kwargs["pk"])
        except Site.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        instance = self.get_object()
        serializer = SiteDetailSerializer(instance)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")

class MetaCorpDetail(generics.RetrieveAPIView):
    serializer_class = MetaCorpDetailSerializer

    def get_object(self):
        try:
            return MetaCorp.objects.get(pk=self.kwargs["pk"])
        except Site.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        instance = self.get_object()
        serializer = MetaCorpDetailSerializer(instance)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")