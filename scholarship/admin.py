from django.contrib import admin
from .models import Scholarship, ScholarshipAttachment, ScholarshipComment


class RichTextAdminMixin:
    class Media:
        js = (
            'https://cdn.ckeditor.com/ckeditor5/41.4.2/classic/ckeditor.js',
            'js/admin-richtext.js',
        )


class ScholarshipAttachmentInline(admin.TabularInline):
    model = ScholarshipAttachment
    extra = 1


@admin.register(Scholarship)
class ScholarshipAdmin(RichTextAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'organization', 'country', 'level', 'deadline', 'is_active']
    list_editable = ['is_active']
    list_filter = ['level', 'is_active', 'country']
    search_fields = ['title', 'organization', 'description', 'country']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ScholarshipAttachmentInline]
    fieldsets = (
        ('Scholarship Information', {'fields': ('title', 'slug', 'organization', 'country', 'level', 'cover_image')}),
        ('Main Content', {'fields': ('description', 'eligibility', 'benefits')}),
        ('Application', {'fields': ('application_url', 'deadline', 'is_active')}),
    )


@admin.register(ScholarshipComment)
class ScholarshipCommentAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'scholarship', 'parent', 'created_at', 'is_approved']
    list_editable = ['is_approved']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['body', 'guest_name', 'scholarship__title']

    def display_name(self, obj):
        return obj.display_name
