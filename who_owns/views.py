from django.http import HttpResponse, Http404

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.renderers import JSONRenderer

from who_owns.models import Filing, Judge, MetaCorp, Institution
from who_owns.serializers import (
    FilingSerializer,
    JudgeSerializer,
    InstitutionPortfolioSerializer,
    InstitutionDetailsSerializer,
)


class InstitutionPortfolioDetail(generics.RetrieveAPIView):
    """
    Output: feature collection with parcel IDs,
    addresses, coordinates, number of units and
    evictions (y/n) for each property owned by the owner)
    """

    def get_object(self):
        return Institution.objects.get(pk=self.kwargs["pk"])

    def get_related_objects(self, metacorp):
        return Institution.objects.filter(metacorp=metacorp)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        related_instances = self.get_related_objects(instance.metacorp)
        serializer = InstitutionPortfolioSerializer(related_instances, many=True)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")


class InstitutionDetail(generics.RetrieveAPIView):
    """
    Owner details:
    Input: Owner ID (unique)
    Output: LLC name, Owner name, evictor type, total number of units,
    total number of properties, code violations (if available),
    lawyer names (if available) other names for the LLCs, # LLCs,
    corporate addresses, total evictions by type,
    """

    serializer_class = InstitutionDetailsSerializer

    def get_object(self):
        return Institution.objects.get(pk=self.kwargs["pk"])

    def get(self, request, pk, format=None):
        instance = self.get_object()
        serializer = InstitutionDetailsSerializer(instance)
        content = JSONRenderer().render(serializer.data)
        return HttpResponse(content, content_type="application/json")


class MetaCorpDetail(APIView):
    def get_object(self, id):
        try:
            return MetaCorp.objects.get(id=id)
        except MetaCorp.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query")
        if query == "portfolio":
            print("getting portfolio")
            data = self.get_portfolio()
        elif query == "details":
            print("getting details")
            data = self.get_details()
        else:
            return Http404
        content = JSONRenderer().render(data)
        return HttpResponse(content, content_type="application/json")

    def get_portfolio(self):
        """
        Output: feature collection with parcel IDs,
        addresses, coordinates, number of units and
        evictions (y/n) for each property owned by the owner)
        """
        print("get_portfolio", self)
        corp_with_portfolio = MetaCorpPortfolioSerializer(self.id)
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
