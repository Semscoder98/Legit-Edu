from rest_framework import serializers
from .models import Post, Category, Tag, Comment


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    tags = TagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'category_id',
            'tags', 'cover_image', 'excerpt', 'body', 'post_type', 'status',
            'is_featured', 'is_breaking', 'views', 'comment_count',
            'created_at', 'updated_at', 'published_at',
        ]
        read_only_fields = ['slug', 'views', 'author', 'published_at']

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()
