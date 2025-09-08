from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Software
from .models_task import InstallationTask
import json
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

@csrf_exempt
@require_http_methods(["GET"])
def get_tasks_for_host(request):
    """Retorna tarefas pendentes para um hostname específico"""
    hostname = request.GET.get('hostname')
    if not hostname:
        return HttpResponseBadRequest('Hostname is required')

    try:
        # Busca tarefas pendentes para este hostname
        tasks = InstallationTask.objects.filter(
            hostname=hostname,
            status='pending'
        ).select_related('software')

        # Converte para formato JSON
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task.id,
                'software': {
                    'name': task.software.name,
                    'version': task.software.version
                },
                'installer_url': task.installer_url,
                'status': task.status,
                'created_at': task.created_at.isoformat(),
                'install_args': task.software.install_args or ''
            })

        return JsonResponse({'tasks': task_list})

    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=500
        )

@csrf_exempt
@require_http_methods(["PATCH"])
def update_task_status(request, task_id):
    """Atualiza o status de uma tarefa"""
    if not request.body:
        return HttpResponseBadRequest('Request body is required')

    try:
        data = json.loads(request.body)
        status = data.get('status')
        log = data.get('log', '')

        if not status:
            return HttpResponseBadRequest('Status is required')

        # Atualiza a tarefa
        with transaction.atomic():
            task = InstallationTask.objects.select_for_update().get(id=task_id)
            task.status = status
            task.log = log
            task.updated_at = timezone.now()
            task.save()

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')
    except InstallationTask.DoesNotExist:
        return JsonResponse(
            {'error': 'Task not found'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=500
        )

@csrf_exempt
@require_http_methods(["POST"])
def create_task(request):
    """Cria uma nova tarefa de instalação"""
    if not request.body:
        return HttpResponseBadRequest('Request body is required')

    try:
        data = json.loads(request.body)
        
        # Valida os dados
        required_fields = ['software_id', 'hostname', 'installer_url']
        for field in required_fields:
            if field not in data:
                return HttpResponseBadRequest(f'{field} is required')

        # Cria a tarefa
        task = InstallationTask(
            software_id=data['software_id'],
            hostname=data['hostname'],
            installer_url=data['installer_url'],
            status='pending'
        )
        task.full_clean()
        task.save()

        return JsonResponse({
            'id': task.id,
            'status': task.status,
            'created_at': task.created_at.isoformat()
        })

    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')
    except ValidationError as e:
        return JsonResponse(
            {'error': e.message_dict},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=500
        )
