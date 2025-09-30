import os
import json
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from ...models import Software

class Command(BaseCommand):
    help = 'Importa softwares a partir de um arquivo JSON ou de um diretório'

    def add_arguments(self, parser):
        parser.add_argument('source', type=str, help='Caminho para o arquivo JSON ou diretório contendo os softwares')
        parser.add_argument('--update', action='store_true', help='Atualiza softwares existentes')

    def handle(self, *args, **options):
        source = options['source']
        update = options['update']

        if os.path.isfile(source) and source.endswith('.json'):
            self.import_from_json(source, update)
        elif os.path.isdir(source):
            self.import_from_directory(source, update)
        else:
            raise CommandError(f'O caminho fornecido não é um arquivo JSON nem um diretório: {source}')

    def import_from_json(self, json_file, update):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    self.create_or_update_software(item, update)
            else:
                self.create_or_update_software(data, update)
            
            self.stdout.write(self.style.SUCCESS(f'Importação concluída a partir de {json_file}'))
        except Exception as e:
            raise CommandError(f'Erro ao importar do arquivo JSON: {str(e)}')

    def import_from_directory(self, directory, update):
        try:
            # Verifica se existe um arquivo metadata.json no diretório
            metadata_file = os.path.join(directory, 'metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Se for uma lista, processa cada item
                if isinstance(metadata, list):
                    for item in metadata:
                        self.process_directory_item(directory, item, update)
                else:
                    self.process_directory_item(directory, metadata, update)
            else:
                # Se não houver metadata.json, tenta importar todos os arquivos do diretório
                for filename in os.listdir(directory):
                    if filename.endswith(('.exe', '.msi', '.msix', '.appx', '.zip')):
                        name = os.path.splitext(filename)[0]
                        version = '1.0.0'  # Versão padrão
                        
                        item = {
                            'name': name,
                            'version': version,
                            'installer': filename,
                            'description': f'Instalador para {name}',
                            'category': 'OTHER',
                            'is_active': True
                        }
                        
                        self.process_directory_item(directory, item, update)
            
            self.stdout.write(self.style.SUCCESS(f'Importação concluída a partir do diretório {directory}'))
        except Exception as e:
            raise CommandError(f'Erro ao importar do diretório: {str(e)}')
    
    def process_directory_item(self, directory, item, update):
        try:
            # Define os caminhos dos arquivos
            installer_path = os.path.join(directory, item.get('installer', ''))
            icon_path = os.path.join(directory, item.get('icon', '')) if item.get('icon') else None
            
            # Verifica se o instalador existe
            if not os.path.exists(installer_path):
                self.stdout.write(self.style.WARNING(f'Instalador não encontrado: {installer_path}'))
                return
            
            # Verifica se o ícone existe
            if icon_path and not os.path.exists(icon_path):
                self.stdout.write(self.style.WARNING(f'Ícone não encontrado: {icon_path}'))
                icon_path = None
            
            # Cria ou atualiza o software
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
            
            # Se o software já existe e a opção --update foi especificada, atualiza
            if not created and update:
                software.description = item.get('description', software.description)
                software.category = item.get('category', software.category)
                software.is_active = item.get('is_active', software.is_active)
                software.install_script = item.get('install_script', software.install_script)
                software.save()
            
            # Atualiza o instalador
            with open(installer_path, 'rb') as f:
                software.installer.save(os.path.basename(installer_path), File(f), save=True)
            
            # Atualiza o ícone se especificado
            if icon_path:
                with open(icon_path, 'rb') as f:
                    software.icon.save(os.path.basename(icon_path), File(f), save=True)
            
            action = 'Atualizado' if not created and update else 'Criado' if created else 'Ignorado (use --update para atualizar)'
            self.stdout.write(self.style.SUCCESS(f'{action}: {software.name} {software.version}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao processar item: {str(e)}'))
