import subprocess
import os
import sys
import requests
import zipfile
import shutil
import time
import json
import psutil
import logging
import re
from pathlib import Path
from threading import Thread
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from instalar_playit import install_playit, is_playit_installed, run_command_async

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).parent / "terraria_config.json"
SCRIPT_DIR = Path(__file__).parent.resolve()
TERRARIA_FOLDER = SCRIPT_DIR / "terraria-server"
NGROK_FOLDER = SCRIPT_DIR / "ngrok"
WORLDS_FOLDER = SCRIPT_DIR / "worlds"
DEFAULT_TERRARIA_WORLDS = Path.home() / ".local" / "share" / "Terraria" / "Worlds"

TERRARIA_URL = "https://terraria.org/api/download/pc-dedicated-server/terraria-server-1455.zip"
NGROK_DOWNLOAD_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip"

NGROK_TOKEN_REGEX = r"^[0-9a-zA-Z_]{32,}$"
DISCORD_WEBHOOK_REGEX = r"^https://discord\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+$"

class ConfigError(Exception):
    pass

class ServerError(Exception):
    pass

def load_config() -> Dict[str, Any]:
    config = {
        'ngrok_token': None,
        'discord_webhook': None
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved_config = json.load(f)
                config.update(saved_config)
                logger.info("Configuración cargada desde archivo")
                
                if config['ngrok_token'] and not re.match(NGROK_TOKEN_REGEX, config['ngrok_token']):
                    raise ConfigError("Formato de token Ngrok inválido")
                    
                if config['discord_webhook'] and not re.match(DISCORD_WEBHOOK_REGEX, config['discord_webhook']):
                    raise ConfigError("Formato de Discord webhook inválido")
                    
        except json.JSONDecodeError:
            logger.error("Archivo de configuración corrupto")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            sys.exit(1)
            
    return config

def save_config(config: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        CONFIG_FILE.chmod(0o600)
        logger.info("Configuración guardada exitosamente")
    except Exception as e:
        logger.error(f"Error guardando configuración: {e}")
        raise ServerError("No se pudo guardar la configuración")

def setup_directories() -> None:
    try:
        WORLDS_FOLDER.mkdir(exist_ok=True, parents=True)
        (TERRARIA_FOLDER / "logs").mkdir(parents=True, exist_ok=True)
        DEFAULT_TERRARIA_WORLDS.parent.mkdir(exist_ok=True, parents=True)
        logger.info("Directorios configurados correctamente")
    except OSError as e:
        logger.error(f"Error creando directorios: {e}")
        raise ServerError("Error en configuración de directorios")

def create_symlink() -> None:
    try:
        WORLDS_FOLDER.mkdir(exist_ok=True, parents=True)
        DEFAULT_TERRARIA_WORLDS.parent.mkdir(exist_ok=True, parents=True)
        
        current_link = None
        if DEFAULT_TERRARIA_WORLDS.exists():
            if DEFAULT_TERRARIA_WORLDS.is_symlink():
                current_link = os.readlink(DEFAULT_TERRARIA_WORLDS)
                if current_link == str(WORLDS_FOLDER):
                    logger.info("Enlace simbólico ya existe y es correcto")
                    return
                
            backup_path = DEFAULT_TERRARIA_WORLDS.with_name(f"{DEFAULT_TERRARIA_WORLDS.name}_backup_{int(time.time())}")
            shutil.move(str(DEFAULT_TERRARIA_WORLDS), str(backup_path))
            logger.info(f"Backup creado en: {backup_path}")

        DEFAULT_TERRARIA_WORLDS.symlink_to(WORLDS_FOLDER)
        logger.info(f"Enlace simbólico creado: {DEFAULT_TERRARIA_WORLDS} -> {WORLDS_FOLDER}")

    except PermissionError as e:
        logger.error(f"Permisos insuficientes: {e}")
        raise ServerError("Error de permisos al crear enlace")
    except OSError as e:
        logger.error(f"Error del sistema: {e}")
        raise ServerError("Error al crear enlace simbólico")

def download_file(url: str, destination: Path, max_retries: int = 3) -> None:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()
            
            with destination.open('wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"Descarga exitosa: {destination.name}")
            return
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Reintentando descarga ({attempt + 1}/{max_retries}) en {wait_time}s...")
                time.sleep(wait_time)
                continue
            logger.error(f"Error al descargar {url}: {e}")
            raise ServerError(f"Fallo en la descarga de {destination.name}")

def setup_terraria_server() -> None:
    if (TERRARIA_FOLDER / "TerrariaServer").exists():
        logger.info("Servidor de Terraria ya instalado")
        return

    zip_path = SCRIPT_DIR / "terraria-server.zip"
    try:
        download_file(TERRARIA_URL, zip_path)
        
        with zipfile.ZipFile(zip_path) as zip_ref:
            zip_ref.extractall(TERRARIA_FOLDER)
            
        binary_path = next(TERRARIA_FOLDER.rglob("TerrariaServer.bin.x86_64"), None)
        if not binary_path:
            raise FileNotFoundError("Binario del servidor no encontrado en el archivo ZIP")
            
        binary_path.chmod(0o755)
        logger.info(f"Binario del servidor encontrado en: {binary_path}")

    except zipfile.BadZipFile:
        logger.error("Archivo ZIP corrupto")
        raise ServerError("Error en el archivo de Terraria")
    finally:
        zip_path.unlink(missing_ok=True)

    create_server_config()

def create_server_config() -> None:
    config_path = TERRARIA_FOLDER / "serverconfig.txt"
    default_config = """# Configuración generada automáticamente
port=7777
motd=¡Bienvenido al servidor!
"""
    
    try:
        with open(config_path, 'w') as f:
            f.write(default_config)
        logger.info(f"Archivo de configuración creado en: {config_path}")
        
        config_path.chmod(0o644)
        
    except IOError as e:
        logger.error(f"Error creando archivo de configuración: {e}")
        raise ServerError("No se pudo crear la configuración del servidor")

def setup_ngrok(config: Dict[str, Any]) -> subprocess.Popen:
    ngrok_executable = NGROK_FOLDER / "ngrok"
    
    if not ngrok_executable.exists():
        zip_path = SCRIPT_DIR / "ngrok.zip"
        download_file(NGROK_DOWNLOAD_URL, zip_path)
        
        with zipfile.ZipFile(zip_path) as zip_ref:
            zip_ref.extractall(NGROK_FOLDER)
            
        ngrok_executable.chmod(0o755)
        zip_path.unlink()

    auth_result = subprocess.run(
        [str(ngrok_executable), "authtoken", config['ngrok_token']],
        capture_output=True,
        text=True
    )
    
    if auth_result.returncode != 0:
        logger.error(f"Error autenticando Ngrok: {auth_result.stderr}")
        raise ServerError("Fallo en autenticación de Ngrok")

    ngrok_process = subprocess.Popen(
        [str(ngrok_executable), "tcp", "7777", "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    tunnel_url = None
    start_time = time.time()
    while time.time() - start_time < 30:
        line = ngrok_process.stdout.readline()
        if "started tunnel" in line and "url=tcp://" in line:
            tunnel_url = line.split("url=tcp://")[1].strip()
            logger.info(f"Túnel Ngrok establecido: tcp://{tunnel_url}")
            print(f"\n[INFO] ¡Servidor listo! Conéctate usando: tcp://{tunnel_url}\n")
            break
            
    if not tunnel_url:
        ngrok_process.terminate()
        raise ServerError("No se pudo obtener URL del túnel Ngrok")
        
    send_to_discord(config.get('discord_webhook'), tunnel_url)
    return ngrok_process

def setup_playit() -> subprocess.Popen:
    if not is_playit_installed():
        logger.info("Instalando Playit...")
        try:
            install_playit()
        except Exception as e:
            logger.error(f"Error instalando Playit: {e}")
            raise ServerError("Instalación de Playit fallida")

    logger.info("Iniciando Playit...")
    try:
        process = run_command_async("playit")
        time.sleep(2)
        
        if not any("playit" in p.name() for p in psutil.process_iter(['name'])):
            raise ServerError("Playit no se inició correctamente")
            
        print("\n[INFO] Playit iniciado correctamente.")
        print("[INFO] Ejecuta 'playit show' en otra terminal para ver la dirección de conexión.")
        print("[INFO] La dirección también aparecerá automáticamente en unos segundos.\n")
        return process
            
    except Exception as e:
        logger.error(f"Error iniciando Playit: {e}")
        raise

def send_to_discord(webhook: Optional[str], full_address: str) -> None:
    if not webhook:
        logger.info("Webhook de Discord no configurado")
        return

    def async_send():
        try:
            if ':' not in full_address:
                raise ValueError("Formato de dirección inválido")
                
            ip, port = full_address.split(':', 1)
            if not port.isdigit():
                raise ValueError("Puerto inválido")

            embed = {
                "title": " Servidor de Terraria Activo ",
                "color": 0x00FF00,
                "fields": [
                    {"name": "IP", "value": f"`{ip}`", "inline": True},
                    {"name": "Puerto", "value": f"`{port}`", "inline": True}
                ],
                "footer": {"text": f"Iniciado: {time.strftime('%Y-%m-%d %H:%M:%S')}"}
            }

            response = requests.post(
                webhook,
                json={"embeds": [embed]},
                timeout=10
            )
            response.raise_for_status()
            logger.info("Notificación enviada a Discord")
            
        except Exception as e:
            logger.error(f"Error enviando a Discord: {e}")

    Thread(target=async_send, daemon=True).start()

def server_monitor() -> None:
    while True:
        time.sleep(300)
        try:
            terraria_processes = [
                p for p in psutil.process_iter(['name'])
                if "TerrariaServer" in p.name()
            ]
            
            if terraria_processes:
                logger.info("Guardando mundo...")
                for p in terraria_processes:
                    p.send_signal(subprocess.signal.SIGUSR1)
        except Exception as e:
            logger.error(f"Error en el monitor: {e}")

def start_terraria_server() -> subprocess.Popen:
    binary_path = next(TERRARIA_FOLDER.rglob("TerrariaServer.bin.x86_64"), None)
    if not binary_path:
        raise ServerError("Ejecutable de Terraria no encontrado")

    config_path = TERRARIA_FOLDER / "serverconfig.txt"
    
    try:
        process = subprocess.Popen(
            [str(binary_path), "-config", str(config_path)],
            cwd=str(binary_path.parent),
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        return process
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {e}")
        raise ServerError("Error en el servidor")

def graceful_shutdown(processes: list) -> None:
    logger.info("Deteniendo procesos...")
    for p in processes:
        try:
            if isinstance(p, subprocess.Popen):
                p.terminate()
                p.wait(timeout=10)
            elif isinstance(p, psutil.Process):
                p.terminate()
        except Exception as e:
            logger.error(f"Error deteniendo proceso {p}: {e}")

def main() -> None:
    processes = []
    try:
        config = load_config()
        setup_directories()
        create_symlink()
        setup_terraria_server()
        
        Thread(target=server_monitor, daemon=True).start()

        while True:
            choice = input("Seleccione túnel [1] Ngrok [2] Playit: ").strip()
            if choice in ('1', '2'):
                break
            logger.error("Opción inválida, intente nuevamente")

        if choice == '1':
            if not config.get('ngrok_token'):
                config['ngrok_token'] = input("Ingrese su token de Ngrok: ").strip()
                if not re.match(NGROK_TOKEN_REGEX, config['ngrok_token']):
                    raise ConfigError("Formato de token Ngrok inválido")
                    
                save_config(config)
                
            webhook = config.get('discord_webhook')
            if not webhook:
                if input("¿Configurar Discord webhook? (s/n): ").lower().startswith('s'):
                    config['discord_webhook'] = input("Ingrese webhook: ").strip()
                    if not re.match(DISCORD_WEBHOOK_REGEX, config['discord_webhook']):
                        raise ConfigError("Formato de webhook inválido")
                    save_config(config)
            
            ngrok_proc = setup_ngrok(config)
            processes.append(ngrok_proc)
            
        elif choice == '2':
            playit_proc = setup_playit()
            if playit_proc:
                processes.append(playit_proc)

        server_proc = start_terraria_server()
        processes.append(server_proc)

        logger.info("Servidor operativo. Presione Ctrl+C para detener.")
        server_proc.wait()

    except (ConfigError, ServerError) as e:
        logger.error(f"Error crítico: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Recibida interrupción, apagando...")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)
    finally:
        graceful_shutdown(processes)

if __name__ == "__main__":
    main()