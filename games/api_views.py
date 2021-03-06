from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import generics, filters
from .serializers import GameSerializer, GameLibrarySerializer

from . import models


class GameListView(generics.GenericAPIView):
    serializer_class = GameSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('slug', )

    def get_queryset(self):
        if 'games' in self.request.GET:
            game_slugs = self.request.GET.getlist('games')
        elif 'games' in self.request.data:
            game_slugs = self.request.data.get('games')
        else:
            game_slugs = []
        if game_slugs:
            queryset = models.Game.objects.filter(slug__in=game_slugs)
        else:
            queryset = models.Game.objects.all()
        return queryset

    def get(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Using POST instead of GET is a violation of API rules but it's the
        # only way to send a huge payload to the server. GET querystrings only
        # support a limited number of characters (depending on the web server or
        # the browser used) whereas POST request do not have this limitation.
        return self.get(request)


class GameLibraryView(generics.RetrieveAPIView):
    serializer_class = GameLibrarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        try:
            library = models.GameLibrary.objects.get(user__username=username)
        except models.GameLibrary.DoesNotExist:
            return Response(status=404)
        serializer = GameLibrarySerializer(library)
        return Response(serializer.data)


class GameDetailView(generics.RetrieveAPIView):
    serializer_class = GameSerializer
    lookup_field = 'slug'
    queryset = models.Game.objects.all()
