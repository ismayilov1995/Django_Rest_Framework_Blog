from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from favorite.models import Favorite


class FavoriteListCreateAPISerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    # Post favlamada istifadeci sehfvi var
    def validate(self, attrs):
        queryset = Favorite.objects.filter(post=attrs['post'], user=attrs['user'])
        if queryset.exists():
            raise serializers.ValidationError("Bu post artiq favlanib")
        return attrs


class FavoriteAPISerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['content']