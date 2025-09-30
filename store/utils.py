import os
import subprocess
import platform
import logging
from django.conf import settings
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

def get_os_info():
    """Obtém informações sobre o sistema operacional."""
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    
    return {
        'system': system,
        'release': release,
        'version': version,
        'machine': machine,
        'is_windows': system == 'Windows',
        'is_linux': system == 'Linux',
        'is_mac': system == 'Darwin',
    }

def execute_install_script(software, user=None):
    """
    Executa o script de instalação de um software.
    
    Args:
        software: Instância do modelo Software
        user: Usuário que está instalando o software (opcional)
    
    Returns:
        tuple: (success, message, output)
    """
    try:
        # Verifica se existe um script de instalação
        if not software.install_script:
            return False, "Nenhum script de instalação definido para este software.", ""
        
        # Obtém informações do sistema operacional
        os_info = get_os_info()
        
        # Cria um arquivo temporário com o script de instalação
        script_ext = '.bat' if os_info['is_windows'] else '.sh'
        script_path = os.path.join(settings.MEDIA_ROOT, 'temp_scripts', f'install_{software.slug}{script_ext}')
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        
        # Escreve o script no arquivo temporário
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(software.install_script)
        
        # Torna o script executável (Unix-like)
        if not os_info['is_windows']:
            os.chmod(script_path, 0o755)
        
        # Executa o script
        if os_info['is_windows']:
            process = subprocess.Popen(
                ['cmd', '/c', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
        else:
            process = subprocess.Popen(
                [script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        # Captura a saída
        stdout, stderr = process.communicate()
        
        # Verifica o código de retorno
        if process.returncode == 0:
            return True, f"{software.name} instalado com sucesso!", stdout
        else:
            return False, f"Erro ao instalar {software.name}.", stderr or stdout
    
    except Exception as e:
        logger.error(f"Erro ao executar script de instalação: {str(e)}", exc_info=True)
        return False, f"Erro inesperado: {str(e)}", ""
    
    finally:
        # Remove o arquivo temporário se existir
        try:
            if os.path.exists(script_path):
                os.remove(script_path)
        except Exception as e:
            logger.error(f"Erro ao remover arquivo temporário: {str(e)}")

def get_file_extension(filename):
    """Obtém a extensão de um arquivo em minúsculas, sem o ponto."""
    return os.path.splitext(filename)[1][1:].lower() if '.' in filename else ''

def validate_file_extension(filename, allowed_extensions):
    """
    Valida se a extensão do arquivo está na lista de extensões permitidas.
    
    Args:
        filename: Nome do arquivo
        allowed_extensions: Lista de extensões permitidas (sem o ponto)
    
    Returns:
        bool: True se a extensão for válida, False caso contrário
    """
    ext = get_file_extension(filename)
    return ext.lower() in [e.lower() for e in allowed_extensions]
