from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Category, Comment, Tag, ContactMessage, TeamMember, NewsletterSubscriber
from .serializers import PostSerializer, CategorySerializer


# ──────────────────── Template Views ────────────────────

def home(request):
    featured = Post.objects.filter(status='published', is_featured=True)[:5]
    breaking = Post.objects.filter(status='published', is_breaking=True)[:5]
    latest = Post.objects.filter(status='published').select_related('author', 'category')[:12]
    categories = Category.objects.all()
    popular = Post.objects.filter(status='published').order_by('-views')[:5]
    thumbnail_posts = Post.objects.filter(status='published').select_related('category').exclude(is_featured=True)[:4]
    return render(request, 'blog/home.html', {
        'featured': featured,
        'breaking': breaking,
        'latest': latest,
        'categories': categories,
        'popular': popular,
        'thumbnail_posts': thumbnail_posts,
    })


def post_list(request):
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    query = request.GET.get('q')
    posts = Post.objects.filter(status='published').select_related('author', 'category')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    else:
        category = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=tag)
    else:
        tag = None

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(body__icontains=query) | Q(excerpt__icontains=query))

    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'active_category': category,
        'active_tag': tag,
        'query': query,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    post.increment_views()
    related = Post.objects.filter(status='published', category=post.category).exclude(pk=post.pk)[:4]
    comments = post.comments.filter(is_approved=True, parent__isnull=True).select_related('author').order_by('created_at')
    comment_count = post.comments.filter(is_approved=True).count()

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        parent_id = request.POST.get('parent_id')
        guest_name = request.POST.get('guest_name', '').strip()
        if body:
            parent = None
            if parent_id:
                parent = Comment.objects.filter(pk=parent_id, post=post).first()
            Comment.objects.create(
                post=post,
                author=request.user if request.user.is_authenticated else None,
                guest_name=guest_name or 'Anonymous',
                body=body,
                parent=parent
            )
            return redirect('post_detail', slug=slug)

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related': related,
        'comments': comments,
        'comment_count': comment_count,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(status='published', category=category)
    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/category_detail.html', {'category': category, 'page_obj': page_obj})


# ──────────────────── REST API ViewSets ────────────────────

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='published').select_related('author', 'category')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'body', 'excerpt']
    ordering_fields = ['created_at', 'views']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


def contact(request):
    form_data = {}
    form_errors = {}
    if request.method == 'POST':
        form_data = {
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'subject': request.POST.get('subject', '').strip(),
            'message': request.POST.get('message', '').strip(),
        }
        if not form_data['name']:
            form_errors['name'] = 'Please enter your name.'
        if not form_data['email']:
            form_errors['email'] = 'Please enter your email address.'
        else:
            try:
                validate_email(form_data['email'])
            except ValidationError:
                form_errors['email'] = 'Please enter a valid email address.'
        if not form_data['message']:
            form_errors['message'] = 'Please enter your message.'

        if not form_errors:
            ContactMessage.objects.create(
                name=form_data['name'],
                email=form_data['email'],
                subject=form_data['subject'] or 'Website Enquiry',
                message=form_data['message'],
            )
            messages.success(request, 'Thank you. Your message has been submitted successfully.')
            return redirect('contact')
    return render(request, 'blog/contact.html', {'form_data': form_data, 'form_errors': form_errors})


def newsletter_subscribe(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Invalid request.'}, status=405)
    email = request.POST.get('email', '').strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'ok': False, 'message': 'Please enter a valid email address.'}, status=400)
    NewsletterSubscriber.objects.update_or_create(email=email, defaults={'is_active': True})
    return JsonResponse({'ok': True, 'message': 'Thank you for subscribing.'})


def about(request):
    team_members = TeamMember.objects.filter(is_active=True)
    return render(request, 'blog/about.html', {'team_members': team_members})


def error_400(request, exception):
    return render(request, 'errors/400.html', status=400)


def error_403(request, exception):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
