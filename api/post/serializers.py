from rest_framework import serializers

from core.models import Tag, Post, Comment


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""
    user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Comment
        fields = ('id', 'content', 'post', 'user', 'created_on')
        read_only_fields = ('id', 'created_on',)


class PostSerializer(serializers.ModelSerializer):
    """Serialize a blog post"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    # comments = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     queryset=Comment.objects.all()
    # )

    class Meta:
        model = Post
        fields = ('id', 'title', 'tags',
                  'content', 'comments', 'link', 'created_on')
        read_only_fields = ('id', 'created_on',)


class CommentDetailSerializer(CommentSerializer):
    """Serialize a post content"""
    post = PostSerializer()


class PostDetailSerializer(PostSerializer):
    """Serialize a post content"""
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True)


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to posts"""

    class Meta:
        model = Post
        fields = ('id', 'image')
        read_only_fields = ('id',)
