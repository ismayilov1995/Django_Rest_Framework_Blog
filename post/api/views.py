from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, CreateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter

from post.api.paginations import PostPagination
from post.api.permissions import IsOwner
from post.models import Post
from post.api.serializers import PostSerializers, PostUpdateCreateSerializers


class PostListAPIView(ListAPIView, CreateModelMixin):
    serializer_class = PostSerializers
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination

    def get_queryset(self):
        queryset = Post.objects.filter(draft=False)
        return queryset

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializers
    lookup_field = 'slug'


class PostUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateCreateSerializers
    lookup_field = 'slug'
    permission_classes = [IsOwner]

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializers
    lookup_field = 'slug'
    permission_classes = [IsOwner]


class PostCreateAPIView(CreateAPIView, ListModelMixin):
    queryset = Post.objects.all()
    serializer_class = PostUpdateCreateSerializers
    permission_classes = [IsAuthenticated]

    # Mixin istifade ederek Createnin icinde siyahilari gosteririrk
    def get(self,request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    # Yeni meqale yaradani istifadecinin adi ile save
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
