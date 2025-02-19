# Servidor de Terraria en Codespaces

Este repositorio contiene un script que te permite configurar y ejecutar un servidor de Terraria utilizando GitHub Codespaces.

---

## 📜 Requisitos

- **GitHub Codespaces:** Es necesaria una cuenta de GitHub con acceso a Codespaces.
- **Credenciales:**
  - Token de Ngrok (si optas por esta opción).
  - Opcionalmente, un webhook de Discord para notificaciones.

---

## 🔧 Instalación y Uso

1. **Descarga los archivos del repositorio:**
   - `setup_terraria.py`
   - `instalar_playit.py`

2. **Ejecuta el script:**
   ```bash
   python setup_terraria.py
   ```

3. **Proceso interactivo:**
   - Se te solicitará elegir entre utilizar **ngrok** o **Playit** para exponer el servidor.
   - Si optas por ngrok, el script te pedirá ingresar tu token y, opcionalmente, la URL de un webhook de Discord para notificaciones.
   - En el caso de Playit, tendrás que obtener la IP correspondiente.

4. **Conéctate al servidor desde Terraria:**
   - Una vez configurado el túnel, se mostrará la dirección (IP y puerto) a la que debes conectarte desde el juego.

---

## 📌 Notas

- **Seguridad:**  
  La configuración se guarda en `terraria_config.json` con permisos restringidos (chmod 600) para proteger tus credenciales.

- **Colaboración:**  
  Este proyecto se encuentra en desarrollo. Todas las contribuciones son bienvenidas. Si encuentras algún inconveniente, por favor, abre un issue.

- **Mantenimiento:**  
  El script incluye un monitor que guarda el mundo automáticamente cada 5 minutos, asegurando la integridad de tu progreso.
