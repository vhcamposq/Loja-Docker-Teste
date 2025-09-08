from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class SoftwareSuggestion(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pendente')
        APPROVED = 'APPROVED', _('Aprovada')
        REJECTED = 'REJECTED', _('Rejeitada')

    title = models.CharField(_('Nome do Software'), max_length=200)
    description = models.TextField(_('Descrição / Justificativa'), blank=True)
    category = models.CharField(_('Categoria sugerida'), max_length=100, blank=True)
    reference_url = models.URLField(_('Link de referência'), blank=True)

    requester = models.ForeignKey(
        User,
        verbose_name=_('Solicitante'),
        on_delete=models.CASCADE,
        related_name='software_suggestions'
    )

    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Sugestão de Software')
        verbose_name_plural = _('Sugestões de Software')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
