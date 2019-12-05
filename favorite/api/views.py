from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from favorite.api.paginations import FavoritePagination
from favorite.api.permissions import IsOwner
from favorite.api.serializers import FavoriteListCreateAPISerializer, FavoriteAPISerializer
from favorite.models import Favorite


class FavoriteListCreateAPIView(ListCreateAPIView):
    serializer_class = FavoriteListCreateAPISerializer
    pagination_class = FavoritePagination
    permission_classes = [IsAuthenticated]

    # Menim favladigim postlari getirir
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    # Neyi ise favlasam menim elediyimi qeyd edir
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteAPISerializer
    lookup_field = 'pk'
    permission_classes = [IsOwner]

