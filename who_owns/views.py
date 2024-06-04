from django.http import HttpResponse, Http404

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.renderers import JSONRenderer

from who_owns.models import Filing, Judge
from who_owns.serializers import FilingSerializer, JudgeSerializer


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
