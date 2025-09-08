# This migration fixes a previously applied initial migration that did not create
# the SoftwareSuggestion table in the database, while the migration state already
# contains the model. We therefore create only the database objects without
# altering the Django state.

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.CreateModel(
                    name='SoftwareSuggestion',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title', models.CharField(max_length=200, verbose_name='Nome do Software')),
                        ('description', models.TextField(blank=True, verbose_name='Descrição / Justificativa')),
                        ('category', models.CharField(blank=True, max_length=100, verbose_name='Categoria sugerida')),
                        ('reference_url', models.URLField(blank=True, verbose_name='Link de referência')),
                        ('status', models.CharField(choices=[('PENDING', 'Pendente'), ('APPROVED', 'Aprovada'), ('REJECTED', 'Rejeitada')], default='PENDING', max_length=20, verbose_name='Status')),
                        ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                        ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                        ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='software_suggestions', to=settings.AUTH_USER_MODEL, verbose_name='Solicitante')),
                    ],
                    options={
                        'verbose_name': 'Sugestão de Software',
                        'verbose_name_plural': 'Sugestões de Software',
                        'ordering': ['-created_at'],
                    },
                ),
                migrations.AddIndex(
                    model_name='softwaresuggestion',
                    index=models.Index(fields=['status'], name='store_softw_status_489a6f_idx'),
                ),
                migrations.AddIndex(
                    model_name='softwaresuggestion',
                    index=models.Index(fields=['created_at'], name='store_softw_created_d5eeae_idx'),
                ),
            ],
            state_operations=[],
        ),
    ]
