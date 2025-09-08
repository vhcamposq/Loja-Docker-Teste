from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Software

User = get_user_model()

class InstallationTask(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pendente')),
        ('in_progress', _('Em progresso')),
        ('completed', _('Concluído')),
        ('error', _('Erro')),
    ]

    software = models.ForeignKey(
        Software,
        on_delete=models.CASCADE,
        verbose_name=_('Software'),
        related_name='installation_tasks'
    )

    hostname = models.CharField(
        _('Hostname'),
        max_length=255,
        db_index=True
    )

    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    installer_url = models.URLField(
        _('URL do Instalador'),
        max_length=500,
        help_text=_('URL para download do instalador')
    )

    log = models.TextField(
        _('Log'),
        blank=True,
        help_text=_('Log da instalação')
    )

    created_at = models.DateTimeField(
        _('Criado em'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('Atualizado em'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Tarefa de Instalação')
        verbose_name_plural = _('Tarefas de Instalação')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hostname', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return f"{self.software.name} - {self.hostname} - {self.get_status_display()}"
