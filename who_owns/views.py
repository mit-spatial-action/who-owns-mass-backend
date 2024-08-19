from django.http import HttpResponse, Http404

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.renderers import JSONRenderer

from who_owns.models import Filing, Judge, MetaCorp, Company
from who_owns.serializers import (
    FilingSerializer,
    JudgeSerializer,
    CompanyPortfolioSerializer,
    CompanyDetailsSerializer,
    MetaCorpSerializer,
    MetaCorpListSerializer,
)


class CompanyPortfolioDetail(generics.RetrieveAPIView):
    """
    Output: feature collection with parcel IDs,
    addresses, coordinates, number of units and
    evictions (y/n) for each property owned by the owner)
    """

    def get_object(self):
        return Company.objects.get(pk=self.kwargs["pk"])

    def get_related_objects(self, metacorp):
        return Company.objects.filter(metacorp=metacorp)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        related_instances = self.get_related_objects(instance.metacorp)
        serializer = CompanyPortfolioSerializer(related_instances, many=True)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")


class CompanyDetail(generics.RetrieveAPIView):
    """
    Owner details:
    Input: Owner ID (unique)
    Output: LLC name, Owner name, evictor type, total number of units,
    total number of properties, code violations (if available),
    lawyer names (if available) other names for the LLCs, # LLCs,
    corporate addresses, total evictions by type,
    """

    serializer_class = CompanyDetailsSerializer
    queryset = Company.objects.all()

    def get(self, request, pk, format=None):
        instance = self.get_object()
        serializer = CompanyDetailsSerializer(instance)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")


class MetaCorpDetail(APIView):
    def get_object(self):
        try:
            return MetaCorp.objects.get(pk=self.kwargs["pk"])
        except MetaCorp.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        instance = self.get_object()
        serializer = MetaCorpSerializer(instance)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")


class MetaCorpList(generics.ListCreateAPIView):
    queryset = MetaCorp.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = MetaCorpListSerializer(
            queryset, context={"request": request}, many=True
        )
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")


class FilingList(generics.ListCreateAPIView):
    queryset = Filing.objects.all()
    serializer_class = FilingSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = FilingSerializer(queryset, many=True)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")


class FilingDetail(APIView):
    def get_object(self, pk):
        try:
            return Filing.objects.get(pk=pk)
        except Filing.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        filing = self.get_object(pk)
        serializer = FilingSerializer(filing)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")


class JudgeList(generics.ListCreateAPIView):
    queryset = Judge.objects.all()
    serializer_class = JudgeSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = JudgeSerializer(queryset, many=True)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")
