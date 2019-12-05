from rest_framework import serializers

from post.models import Post


class PostSerializers(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='post:detail',lookup_field = 'slug')

    username = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['title','content','image','url','created','username','modified_by']

    def get_username(self, obj):
        return str(obj.user.username)

class PostUpdateCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title','content','image']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def validate_title(self, value):
        if value == "duck":
            raise serializers.ValidationError("Bele olmaz, bele yaramaz.")
        return value

    #def validated(self, attrs):
    #    return attrs

    """
    # Yeni meqale yaradarken hansi istifadecinin yaratdigini gostermek
    def create(self, validated_data):
        return Post.objects.create(user=self.context["request"].user, **validated_data)
    """