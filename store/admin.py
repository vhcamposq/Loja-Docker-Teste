from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin import ModelAdmin, site, register
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Software
from .models_suggestion import SoftwareSuggestion
from .admin_views import import_software_view, export_software_view
from .admin_actions import (
    activate_software, deactivate_software, export_selected_software,
    duplicate_software, cleanup_old_versions, mark_as_featured
)
from .admin_filters import (
    ActiveFilter, FeaturedFilter, RecentFilter,
    CategoryFilter, HasIconFilter, HasInstallerFilter
)

@register(Software)
class SoftwareAdmin(ModelAdmin):
    list_display = ('name', 'version', 'category_display', 'is_active', 'created_at', 'download_count')
    list_filter = (
        ActiveFilter,
        FeaturedFilter,
        RecentFilter,
        CategoryFilter,
        HasIconFilter,
        HasInstallerFilter,
        'created_at',
    )
    search_fields = ('name', 'description', 'version')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'preview_icon', 'download_count')
    list_per_page = 25
    actions = [
        activate_software,
        deactivate_software,
        export_selected_software,
        duplicate_software,
        cleanup_old_versions,
        mark_as_featured,
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'version', 'description', 'category', 'is_active', 'is_featured')
        }),
        ('Arquivos', {
            'fields': ('icon', 'preview_icon', 'installer')
        }),
        ('Script de Instalação', {
            'fields': ('install_script', 'install_args'),
            'classes': ('collapse',)
        }),
        ('Estatísticas', {
            'fields': ('download_count',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-software/',
                self.admin_site.admin_view(import_software_view),
                name='import_software',
            ),
            path(
                'export-software/',
                self.admin_site.admin_view(export_software_view),
                name='export_software',
            ),
        ]
        return custom_urls + urls
        
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filtra apenas softwares ativos para usuários não staff
        if not request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_export_buttons'] = True
        
        # Adiciona estatísticas ao contexto
        stats = {
            'total_software': Software.objects.count(),
            'active_software': Software.objects.filter(is_active=True).count(),
            'featured_software': Software.objects.filter(is_featured=True).count(),
            'recent_software': Software.objects.order_by('-created_at')[:5],
        }
        extra_context.update(stats)
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def category_display(self, obj):
        return obj.get_category_display()
    category_display.short_description = 'Categoria'
    category_display.admin_order_field = 'category'
    
    def preview_icon(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" class="img-thumbnail" />',
                obj.icon.url
            )
        return format_html('<span class="text-muted">Sem ícone</span>')
    preview_icon.short_description = 'Ícone'
    preview_icon.allow_tags = True
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove a ação de deleção se o usuário não tiver permissão
        if 'delete_selected' in actions and not request.user.has_perm('store.delete_software'):
            del actions['delete_selected']
        return actions
    
    def has_add_permission(self, request):
        return request.user.has_perm('store.add_software')
    
    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('store.change_software')
    
    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('store.delete_software')
    
    def has_module_permission(self, request):
        return request.user.has_module_perms('store')

# Configurações do site admin
admin.site.site_header = 'Painel de Controle da Loja de Software'
admin.site.site_title = 'Loja de Software - Administração'
admin.site.index_title = 'Visão Geral'
admin.site.site_url = '/'

# Configurações adicionais do admin podem ser adicionadas aqui

@register(SoftwareSuggestion)
class SoftwareSuggestionAdmin(ModelAdmin):
    list_display = ('title', 'requester', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'requester__username', 'requester__email')
    readonly_fields = ('created_at', 'updated_at')
