from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import os


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_ATTACHMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024


def validate_uploaded_file(uploaded_file, allowed_extensions, max_size, label):
    if not uploaded_file:
        return
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in allowed_extensions:
        allowed = ', '.join(sorted(allowed_extensions))
        raise ValidationError(f'{label} must be one of these file types: {allowed}.')
    if getattr(uploaded_file, 'size', 0) and uploaded_file.size > max_size:
        raise ValidationError(f'{label} is too large. Maximum allowed size is {max_size // (1024 * 1024)}MB.')


def unique_slugify(instance, value):
    base_slug = slugify(value)[:250] or 'scholarship'
    slug = base_slug
    counter = 2
    while instance.__class__.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        suffix = f'-{counter}'
        slug = f'{base_slug[:250-len(suffix)]}{suffix}'
        counter += 1
    return slug


class Scholarship(models.Model):
    LEVEL_CHOICES = [
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('phd', 'PhD'),
        ('any', 'Any Level'),
    ]
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=300)
    organization = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='any')
    description = models.TextField(help_text='You can format this scholarship post with the rich editor.')
    eligibility = models.TextField()
    benefits = models.TextField()
    application_url = models.URLField()
    deadline = models.DateField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='scholarships/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        validate_uploaded_file(self.cover_image, ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE, 'Cover image')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)


class ScholarshipAttachment(models.Model):
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=150, blank=True)
    file = models.FileField(upload_to='scholarships/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        validate_uploaded_file(self.file, ALLOWED_ATTACHMENT_EXTENSIONS, MAX_ATTACHMENT_SIZE, 'Attachment')

    def __str__(self):
        return self.title or self.file.name


class ScholarshipComment(models.Model):
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='comments')
    guest_name = models.CharField(max_length=80, blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    @property
    def display_name(self):
        return self.guest_name or 'Anonymous'

    @property
    def flat_replies(self):
        """Return all approved replies under this comment in one flat list.
        Replies remain visually under the main comment while @mentioning
        the exact comment/user being replied to.
        """
        items = []
        for reply in self.replies.filter(is_approved=True).select_related('parent').order_by('created_at'):
            items.append(reply)
            items.extend(reply.flat_replies)
        return items

    def __str__(self):
        return f'Comment by {self.display_name} on {self.scholarship}'
