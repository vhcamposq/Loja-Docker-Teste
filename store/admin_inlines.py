from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Software, SoftwareDownload

class SoftwareDownloadInline(admin.TabularInline):
    """Inline para exibir os downloads de um software."""
    model = SoftwareDownload
    extra = 0
    readonly_fields = ('user', 'downloaded_at', 'ip_address', 'user_agent')
    can_delete = False
    max_num = 5
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False

class SoftwareVersionInline(admin.StackedInline):
    """Inline para gerenciar versões anteriores do software."""
    model = Software
    extra = 0
    fields = ('version', 'release_notes', 'created_at', 'is_active')
    readonly_fields = ('created_at',)
    show_change_link = True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Pega apenas versões mais antigas que a versão atual
        if 'object_id' in request.resolver_match.kwargs:
            current = Software.objects.get(pk=request.resolver_match.kwargs['object_id'])
            return qs.filter(name=current.name, created_at__lt=current.created_at)
        return qs.none()

class RelatedSoftwareInline(admin.TabularInline):
    """Inline para gerenciar softwares relacionados."""
    model = Software.related_software.through
    fk_name = 'from_software'
    extra = 1
    verbose_name = _('Software Relacionado')
    verbose_name_plural = _('Softwares Relacionados')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filtra para não permitir relacionar o software com ele mesmo
        if db_field.name == 'to_software' and 'object_id' in request.resolver_match.kwargs:
            kwargs['queryset'] = Software.objects.exclude(
                pk=request.resolver_match.kwargs['object_id']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SoftwareScreenshotInline(admin.TabularInline):
    """Inline para adicionar screenshots do software."""
    model = 'store.SoftwareScreenshot'
    extra = 1
    fields = ('image', 'caption', 'order')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Define o software atual como padrão para o campo de software
        if db_field.name == 'software' and 'object_id' in request.resolver_match.kwargs:
            kwargs['initial'] = request.resolver_match.kwargs['object_id']
            return db_field.formfield(**kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
