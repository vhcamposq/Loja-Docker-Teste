from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from datetime import datetime, timedelta

def activate_software(modeladmin, request, queryset):
    """Ação para ativar softwares selecionados."""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request, 
        _('{0} software(s) ativado(s) com sucesso.').format(updated),
        messages.SUCCESS
    )

activate_software.short_description = _("Ativar softwares selecionados")


def deactivate_software(modeladmin, request, queryset):
    """Ação para desativar softwares selecionados."""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(
        request, 
        _('{0} software(s) desativado(s) com sucesso.').format(updated),
        messages.SUCCESS
    )

deactivate_software.short_description = _("Desativar softwares selecionados")


def export_selected_software(modeladmin, request, queryset):
    """Ação para exportar softwares selecionados."""
    # Esta ação será tratada na view de exportação
    software_ids = queryset.values_list('id', flat=True)
    request.session['export_software_ids'] = list(software_ids)
    return None

export_selected_software.short_description = _("Exportar softwares selecionados")


def duplicate_software(modeladmin, request, queryset):
    """Ação para duplicar softwares selecionados."""
    for software in queryset:
        software.pk = None
        software.name = f"{software.name} (Cópia)"
        software.slug = f"{software.slug}-copia-{datetime.now().strftime('%Y%m%d')}"
        software.is_active = False
        software.save()
    
    modeladmin.message_user(
        request, 
        _('{0} software(s) duplicado(s) com sucesso.').format(queryset.count()),
        messages.SUCCESS
    )

duplicate_software.short_description = _("Duplicar softwares selecionados")


def cleanup_old_versions(modeladmin, request, queryset):
    """Ação para limpar versões antigas dos softwares."""
    # Mantém apenas a versão mais recente de cada software
    from .models import Software
    
    # Agrupa por nome do software
    software_names = set(queryset.values_list('name', flat=True))
    deleted_count = 0
    
    for name in software_names:
        # Pega a versão mais recente
        latest = Software.objects.filter(name=name).order_by('-created_at').first()
        if latest:
            # Deleta versões mais antigas
            deleted = Software.objects.filter(
                name=name
            ).exclude(
                pk=latest.pk
            ).delete()
            deleted_count += deleted[0]
    
    modeladmin.message_user(
        request, 
        _('{0} versões antigas removidas com sucesso.').format(deleted_count),
        messages.SUCCESS
    )

cleanup_old_versions.short_description = _("Limpar versões antigas")


def mark_as_featured(modeladmin, request, queryset):
    """Marca softwares como em destaque."""
    updated = queryset.update(is_featured=True)
    modeladmin.message_user(
        request, 
        _('{0} software(s) marcado(s) como destaque.').format(updated),
        messages.SUCCESS
    )

mark_as_featured.short_description = _("Marcar como destaque")
