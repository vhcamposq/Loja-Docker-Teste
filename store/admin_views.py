import os
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Software

@staff_member_required
def import_software_view(request):
    """View para importar softwares via interface administrativa."""
    if request.method == 'POST':
        try:
            # Verifica se foi enviado um arquivo
            if 'json_file' in request.FILES:
                json_file = request.FILES['json_file']
                if not json_file.name.endswith('.json'):
                    messages.error(request, 'Por favor, envie um arquivo JSON válido.')
                    return redirect('store:import_software')
                
                # Salva o arquivo temporariamente
                temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'import', json_file.name)
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                
                with open(temp_path, 'wb+') as destination:
                    for chunk in json_file.chunks():
                        destination.write(chunk)
                
                # Lê o conteúdo do arquivo JSON
                with open(temp_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Remove o arquivo temporário
                os.remove(temp_path)
                
                # Processa os dados
                success_count = 0
                error_count = 0
                
                if isinstance(data, list):
                    items = data
                else:
                    items = [data]
                
                for item in items:
                    try:
                        # Verifica se o software já existe
                        software, created = Software.objects.get_or_create(
                            name=item['name'],
                            version=item.get('version', '1.0.0'),
                            defaults={
                                'description': item.get('description', ''),
                                'category': item.get('category', 'OTHER'),
                                'is_active': item.get('is_active', True),
                                'install_script': item.get('install_script', '')
                            }
                        )
                        
                        # Se o software já existe, atualiza os dados
                        if not created and request.POST.get('update_existing', False):
                            software.description = item.get('description', software.description)
                            software.category = item.get('category', software.category)
                            software.is_active = item.get('is_active', software.is_active)
                            software.install_script = item.get('install_script', software.install_script)
                            software.save()
                        
                        # Processa o instalador, se fornecido
                        if 'installer' in request.FILES.getlist('installer_files'):
                            installer_file = request.FILES.get('installer_files')
                            software.installer.save(
                                installer_file.name,
                                ContentFile(installer_file.read()),
                                save=True
                            )
                        
                        # Processa o ícone, se fornecido
                        if 'icon' in request.FILES.getlist('icon_files'):
                            icon_file = request.FILES.get('icon_files')
                            software.icon.save(
                                icon_file.name,
                                ContentFile(icon_file.read()),
                                save=True
                            )
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        messages.error(request, f'Erro ao importar {item.get("name", "item")}: {str(e)}')
                
                messages.success(request, f'Importação concluída: {success_count} itens importados com sucesso, {error_count} erros.')
                
            else:
                messages.error(request, 'Nenhum arquivo enviado.')
                
        except Exception as e:
            messages.error(request, f'Erro ao processar o arquivo: {str(e)}')
        
        return redirect('store:import_software')
    
    return render(request, 'admin/store/import_software.html', {
        'title': 'Importar Softwares',
        'opts': Software._meta,
    })

@staff_member_required
def export_software_view(request):
    """View para exportar softwares para um arquivo JSON."""
    softwares = Software.objects.all().values(
        'name', 'slug', 'description', 'version', 'category',
        'install_script', 'is_active', 'created_at', 'updated_at'
    )
    
    # Converte QuerySet para lista
    data = list(softwares)
    
    # Cria a resposta com o arquivo JSON
    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = 'attachment; filename=software_export.json'
    return response
