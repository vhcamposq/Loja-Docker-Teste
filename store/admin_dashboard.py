from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import Software

class AdminDashboard(admin.AdminSite):
    site_header = 'Painel de Controle da Loja de Software'
    site_title = 'Loja de Software - Administração'
    index_title = 'Visão Geral'
    
    def index(self, request, extra_context=None):
        """Personaliza a página inicial do painel administrativo."""
        extra_context = extra_context or {}
        
        # Estatísticas básicas
        total_softwares = Software.objects.count()
        active_softwares = Software.objects.filter(is_active=True).count()
        
        # Contagem por categoria
        categories = Software.objects.values('category').annotate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True))
        )
        
        # Últimos softwares adicionados
        recent_softwares = Software.objects.order_by('-created_at')[:5]
        
        extra_context.update({
            'total_softwares': total_softwares,
            'active_softwares': active_softwares,
            'categories': categories,
            'recent_softwares': recent_softwares,
        })
        
        return super().index(request, extra_context)

# Cria uma instância personalizada do AdminSite
admin_site = AdminDashboard(name='admin_dashboard')

# Registra os modelos no painel personalizado
@admin.register(Software, site=admin_site)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'category_display', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'version')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'description', 'category', 'is_active')
        }),
        ('Arquivos', {
            'fields': ('icon', 'installer')
        }),
        ('Script de Instalação', {
            'fields': ('install_script',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def category_display(self, obj):
        return obj.get_category_display()
    category_display.short_description = 'Categoria'
