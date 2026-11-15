from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Post, Category, Tag, Comment, PostAttachment, ContactMessage, TeamMember, NewsletterSubscriber


class RichTextAdminMixin:
    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/41.4.2/classic/ckeditor.js',
            'js/admin-richtext.js',
        )


class PostAttachmentInline(admin.TabularInline):
    model = PostAttachment
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        return obj.posts.count()

    def delete_model(self, request, obj):
        if obj.posts.exists():
            self.message_user(request, 'This category still has posts. Move or delete those posts first.', messages.ERROR)
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        blocked = queryset.filter(posts__isnull=False).distinct()
        if blocked.exists():
            self.message_user(request, 'Some selected categories still have posts and were not deleted.', messages.ERROR)
            queryset = queryset.exclude(pk__in=blocked.values_list('pk', flat=True))
        super().delete_queryset(request, queryset)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(RichTextAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'is_breaking', 'show_registration_help', 'notify_subscribers', 'views', 'created_at']
    list_filter = ['status', 'is_featured', 'is_breaking', 'show_registration_help', 'notify_subscribers', 'category', 'post_type']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured', 'is_breaking', 'show_registration_help', 'notify_subscribers']
    date_hierarchy = 'created_at'
    filter_horizontal = ['tags']
    inlines = [PostAttachmentInline]
    fieldsets = (
        ('Post Information', {'fields': ('title', 'slug', 'author', 'category', 'tags', 'cover_image', 'excerpt')}),
        ('Main Content', {'fields': ('body',)}),
        ('Publishing', {'fields': ('post_type', 'status', 'is_featured', 'is_breaking', 'show_registration_help', 'notify_subscribers', 'published_at')}),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'post', 'parent', 'created_at', 'is_approved']
    list_editable = ['is_approved']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['body', 'guest_name', 'author__username', 'post__title']

    def display_name(self, obj):
        return obj.display_name


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['preview', 'name', 'role', 'is_active', 'order']
    list_display_links = ['preview', 'name']
    list_editable = ['is_active', 'order']
    search_fields = ['name', 'role']

    def preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:50%;" />', obj.photo.url)
        return '-'
    preview.short_description = 'Photo'


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['email']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_editable = ['is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
