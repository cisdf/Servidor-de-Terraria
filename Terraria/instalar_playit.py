import subprocess
import os
import signal
import sys

def run_command(command):
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Éxito: {result.stdout}")
    print("-" * 50)

def run_command_async(command):
    print(f"Ejecutando de forma asíncrona: {command}")
    return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def is_playit_installed():
    result = subprocess.run("which playit", shell=True, capture_output=True, text=True)
    return result.returncode == 0

def add_to_crontab():
    script_path = os.path.abspath(__file__)
    cron_job = f"@reboot /usr/bin/python3 {script_path}"
    
    result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
    current_cron = result.stdout if result.returncode == 0 else ""
    
    if cron_job in current_cron:
        print("El cron job ya está presente.")
    else:
        print("Añadiendo el cron job al crontab...")
        new_cron = current_cron.strip() + "\n" + cron_job + "\n"
        process = subprocess.run("crontab -", input=new_cron, shell=True, text=True)
        if process.returncode == 0:
            print("Cron job añadido exitosamente.")
        else:
            print("Error al añadir el cron job.")

def install_playit():
    commands = [
        "curl -SsL https://playit-cloud.github.io/ppa/key.gpg | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/playit.gpg >/dev/null",
        'echo "deb [signed-by=/etc/apt/trusted.gpg.d/playit.gpg] https://playit-cloud.github.io/ppa/data ./" | sudo tee /etc/apt/sources.list.d/playit-cloud.list',
        "sudo apt update",
        "sudo apt install playit -y"
    ]
    for cmd in commands:
        run_command(cmd)

def stop_playit(signal, frame):
    print("Cerrando el proceso de Playit...")
    subprocess.run("pkill playit", shell=True)
    sys.exit(0)

def main():
    signal.signal(signal.SIGTERM, stop_playit)

    if is_playit_installed():
        print("Playit ya está instalado. Iniciando Playit...")
    else:
        print("Playit no está instalado. Iniciando instalación...")
        install_playit()

    process = run_command_async("nohup playit > /dev/null 2>&1 &")

    add_to_crontab()

    print("Proceso completado. Esperando cierre de terminal...")

    process.wait()

if __name__ == "__main__":
    main()