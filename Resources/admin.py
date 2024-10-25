<<<<<<< HEAD
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Resource, CustomUser, Category, Comment

class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ('title', 'resource_type', 'date_uploaded', 'is_approved')
    readonly_fields = ('date_uploaded',)
    show_change_link = True

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('content', 'user', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'phone_number', 
        'is_staff', 
        'date_joined', 
        'resource_count'
    ]
    list_filter = UserAdmin.list_filter + ('date_joined',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('phone_number', 'bio')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('phone_number', 'bio')
        }),
    )
    
    inlines = [ResourceInline]

    def resource_count(self, obj):
        return obj.resources.count()
    resource_count.short_description = 'Resources'

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'resource_type',
        'uploaded_by_link',
        'date_uploaded',
        'is_approved',
        'views_count',
        'comments_count'
    )
    list_filter = ('resource_type', 'category', 'is_approved', 'date_uploaded')
    search_fields = ('title', 'description', 'uploaded_by__username', 'category__name')
    readonly_fields = ('date_uploaded', 'date_updated', 'views_count')
    autocomplete_fields = ['uploaded_by', 'category']
    date_hierarchy = 'date_uploaded'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'uploaded_by', 'category')
        }),
        ('Resource Details', {
            'fields': ('resource_type', 'file', 'external_link')
        }),
        ('Status and Metrics', {
            'fields': ('is_approved', 'date_uploaded', 'date_updated', 'views_count'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CommentInline]
    
    def uploaded_by_link(self, obj):
        # Fix: Update the URL pattern to include the correct app name
        url = reverse('admin:%s_%s_change' % (
            obj.uploaded_by._meta.app_label,
            obj.uploaded_by._meta.model_name
        ), args=[obj.uploaded_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.username)
    uploaded_by_link.short_description = 'Uploaded By'
    
    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Comments'
    
    actions = ['approve_resources', 'unapprove_resources']
    
    def approve_resources(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} resources were successfully approved.')
    approve_resources.short_description = "Approve selected resources"
    
    def unapprove_resources(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} resources were successfully unapproved.')
    unapprove_resources.short_description = "Unapprove selected resources"
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'resource_count')
    search_fields = ('name', 'description')
    
    def resource_count(self, obj):
        return obj.resources.count()
    resource_count.short_description = 'Number of Resources'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'resource', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username', 'resource__title')
    readonly_fields = ('created_at',)
    
    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
=======
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Resource, CustomUser, Category, Comment

class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ('title', 'resource_type', 'date_uploaded', 'is_approved')
    readonly_fields = ('date_uploaded',)
    show_change_link = True

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('content', 'user', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'phone_number', 
        'is_staff', 
        'date_joined', 
        'resource_count'
    ]
    list_filter = UserAdmin.list_filter + ('date_joined',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('phone_number', 'bio')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('phone_number', 'bio')
        }),
    )
    
    inlines = [ResourceInline]

    def resource_count(self, obj):
        return obj.resources.count()
    resource_count.short_description = 'Resources'

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'resource_type',
        'uploaded_by_link',
        'date_uploaded',
        'is_approved',
        'views_count',
        'comments_count'
    )
    list_filter = ('resource_type', 'category', 'is_approved', 'date_uploaded')
    search_fields = ('title', 'description', 'uploaded_by__username', 'category__name')
    readonly_fields = ('date_uploaded', 'date_updated', 'views_count')
    autocomplete_fields = ['uploaded_by', 'category']
    date_hierarchy = 'date_uploaded'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'uploaded_by', 'category')
        }),
        ('Resource Details', {
            'fields': ('resource_type', 'file', 'external_link')
        }),
        ('Status and Metrics', {
            'fields': ('is_approved', 'date_uploaded', 'date_updated', 'views_count'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CommentInline]
    
    def uploaded_by_link(self, obj):
        # Fix: Update the URL pattern to include the correct app name
        url = reverse('admin:%s_%s_change' % (
            obj.uploaded_by._meta.app_label,
            obj.uploaded_by._meta.model_name
        ), args=[obj.uploaded_by.id])
        return format_html('<a href="{}">{}</a>', url, obj.uploaded_by.username)
    uploaded_by_link.short_description = 'Uploaded By'
    
    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Comments'
    
    actions = ['approve_resources', 'unapprove_resources']
    
    def approve_resources(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} resources were successfully approved.')
    approve_resources.short_description = "Approve selected resources"
    
    def unapprove_resources(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} resources were successfully unapproved.')
    unapprove_resources.short_description = "Unapprove selected resources"
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'resource_count')
    search_fields = ('name', 'description')
    
    def resource_count(self, obj):
        return obj.resources.count()
    resource_count.short_description = 'Number of Resources'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'resource', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username', 'resource__title')
    readonly_fields = ('created_at',)
    
    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
>>>>>>> 7cc8ac5 (uploaded the resources app)
    truncated_content.short_description = 'Comment'