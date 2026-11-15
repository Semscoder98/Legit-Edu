from .models import Category, Post


def sidebar_context(request):
    return {
        'all_categories': Category.objects.all(),
        'popular_posts': Post.objects.filter(status='published').order_by('-views')[:5],
        'recent_posts': Post.objects.filter(status='published').order_by('-created_at')[:5],
    }
