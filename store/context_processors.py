from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from .models import Software

def categories(request):
    """Adiciona a lista de categorias ao contexto de todos os templates."""
    return {
        'all_categories': dict(Software.CATEGORY_CHOICES),
    }

def active_software_count(request):
    """Adiciona a contagem de softwares ativos ao contexto."""
    return {
        'active_software_count': Software.objects.filter(is_active=True).count(),
    }

def software_stats(request):
    """Adiciona estatísticas de softwares ao contexto."""
    if not request.user.is_staff:
        return {}
        
    stats = {
        'total_software': Software.objects.count(),
        'active_software': Software.objects.filter(is_active=True).count(),
        'software_by_category': Software.objects.values('category')
                                            .annotate(count=Count('id'))
                                            .order_by('-count'),
    }
    
    return {'software_stats': stats}

def admin_extra_context(request):
    """Adiciona contexto extra para o painel administrativo."""
    if not request.path.startswith('/admin/'):
        return {}
        
    return {
        'site_header': 'Painel de Controle - Loja de Software',
        'site_title': 'Loja de Software - Administração',
        'site_url': '/',
        'has_permission': request.user.is_active and request.user.is_staff,
        'is_popup': False,
        'available_apps': [],
    }

def debug_info(request):
    """Adiciona informações de depuração ao contexto (apenas em DEBUG)."""
    if not settings.DEBUG:
        return {}
        
    return {
        'debug': True,
        'sql_queries': getattr(request, 'sql_queries', None),
    }
