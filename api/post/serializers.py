from rest_framework import serializers

from core.models import Tag, Post


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class PostSerializer(serializers.ModelSerializer):
    """Serialize a blog post"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Post
        fields = ('id', 'title', 'tags',
                  'content', 'link')
        read_only_fields = ('id',)


class PostDetailSerializer(PostSerializer):
    """Serialize a post content"""
    tags = TagSerializer(many=True, read_only=True)


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to posts"""

    class Meta:
        model = Post
        fields = ('id', 'image')
        read_only_fields = ('id',)