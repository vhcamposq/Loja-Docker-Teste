from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from datetime import datetime, timedelta

class ActiveFilter(admin.SimpleListFilter):
    title = _('Status')
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Ativo')),
            ('0', _('Inativo')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_active=True)
        if self.value() == '0':
            return queryset.filter(is_active=False)

class FeaturedFilter(admin.SimpleListFilter):
    title = _('Destaque')
    parameter_name = 'is_featured'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Sim')),
            ('0', _('Não')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_featured=True)
        if self.value() == '0':
            return queryset.filter(is_featured=False)

class RecentFilter(admin.SimpleListFilter):
    title = _('Recente')
    parameter_name = 'recent'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Adicionados hoje')),
            ('week', _('Últimos 7 dias')),
            ('month', _('Últimos 30 dias')),
        )

    def queryset(self, request, queryset):
        today = datetime.now().date()
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=today)
        
        if self.value() == 'week':
            week_ago = today - timedelta(days=7)
            return queryset.filter(created_at__date__gte=week_ago)
        
        if self.value() == 'month':
            month_ago = today - timedelta(days=30)
            return queryset.filter(created_at__date__gte=month_ago)

class CategoryFilter(admin.SimpleListFilter):
    title = _('Categoria')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        from .models import Software
        return Software.CATEGORY_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category=self.value())

class HasIconFilter(admin.SimpleListFilter):
    title = _('Tem ícone')
    parameter_name = 'has_icon'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Sim')),
            ('0', _('Não')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.exclude(icon='')
        if self.value() == '0':
            return queryset.filter(icon='')

class HasInstallerFilter(admin.SimpleListFilter):
    title = _('Tem instalador')
    parameter_name = 'has_installer'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Sim')),
            ('0', _('Não')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.exclude(installer='')
        if self.value() == '0':
            return queryset.filter(installer='')
