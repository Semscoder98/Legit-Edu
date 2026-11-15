from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
import os


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_ATTACHMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB


def validate_uploaded_file(uploaded_file, allowed_extensions, max_size, label):
    if not uploaded_file:
        return
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in allowed_extensions:
        allowed = ', '.join(sorted(allowed_extensions))
        raise ValidationError(f'{label} must be one of these file types: {allowed}.')
    if getattr(uploaded_file, 'size', 0) and uploaded_file.size > max_size:
        raise ValidationError(f'{label} is too large. Maximum allowed size is {max_size // (1024 * 1024)}MB.')


def unique_slugify(instance, value, slug_field='slug'):
    base_slug = slugify(value)[:250] or 'item'
    slug = base_slug
    Model = instance.__class__
    counter = 2
    while Model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        suffix = f'-{counter}'
        slug = f'{base_slug[:250-len(suffix)]}{suffix}'
        counter += 1
    return slug
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published')]
    POST_TYPE = [('news', 'News'), ('jamb', 'JAMB'), ('general', 'General')]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=300)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True)
    cover_image = models.ImageField(upload_to='blog/covers/', blank=True, null=True)
    excerpt = models.TextField(max_length=500, blank=True)
    body = models.TextField(help_text='You can format this post with the rich editor.')
    post_type = models.CharField(max_length=20, choices=POST_TYPE, default='general')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_breaking = models.BooleanField(default=False, help_text='Show in breaking news ticker')
    show_registration_help = models.BooleanField(default=False, help_text='Show WhatsApp registration/admission help box at the bottom of this post')
    notify_subscribers = models.BooleanField(default=False, help_text='Email newsletter subscribers when this post is published')
    newsletter_sent_at = models.DateTimeField(null=True, blank=True, editable=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        validate_uploaded_file(self.cover_image, ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE, 'Cover image')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
        if self.status == 'published' and self.notify_subscribers and not self.newsletter_sent_at:
            try:
                subscribers = NewsletterSubscriber.objects.filter(is_active=True).values_list('email', flat=True)
                post_url = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/blog/{self.slug}/"
                for email in subscribers:
                    send_mail(
                        subject=f'New update from LegitEdu: {self.title}',
                        message=f'{self.excerpt or self.title}\n\nRead more: {post_url}',
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'legiteduconsults@gmail.com'),
                        recipient_list=[email],
                        fail_silently=True,
                    )
                self.newsletter_sent_at = timezone.now()
                Post.objects.filter(pk=self.pk).update(newsletter_sent_at=self.newsletter_sent_at)
            except Exception:
                pass

    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(views=models.F('views') + 1)


class PostAttachment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=150, blank=True)
    file = models.FileField(upload_to='blog/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        validate_uploaded_file(self.file, ALLOWED_ATTACHMENT_EXTENSIONS, MAX_ATTACHMENT_SIZE, 'Attachment')

    def __str__(self):
        return self.title or self.file.name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    guest_name = models.CharField(max_length=80, blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    @property
    def display_name(self):
        if self.author:
            return self.author.get_full_name() or self.author.username
        return self.guest_name or 'Anonymous'

    @property
    def flat_replies(self):
        """Return all approved replies under this comment in one flat list.
        This keeps replies directly under the main comment while preserving
        the exact @name of the comment being replied to.
        """
        items = []
        for reply in self.replies.filter(is_approved=True).select_related('author', 'parent', 'parent__author').order_by('created_at'):
            items.append(reply)
            items.extend(reply.flat_replies)
        return items

    def __str__(self):
        return f'Comment by {self.display_name} on {self.post}'


class TeamMember(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    facebook = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.subject}'
