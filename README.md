# Servidor de Terraria en Codespaces

Este repositorio contiene un script para configurar y ejecutar un servidor de Terraria en GitHub Codespaces.

---

## 📜 Requisitos

- **GitHub Codespaces:** Se necesita una cuenta de GitHub con acceso a Codespaces.
- **Credenciales:**  
  - Token de Ngrok (si eliges esta opción).
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
   - Se te pedirá elegir entre utilizar **ngrok** o **Playit** para exponer el servidor.
   - Si eliges ngrok, el script solicitará tu token y, opcionalmente, la URL de un webhook de Discord para notificaciones.
   - En el caso de Playit, trendras que consegir la ip de playit.

4. **Conéctate al servidor desde Terraria:**
   - Una vez configurado el túnel, se mostrará la dirección (IP y puerto) a la que debes conectarte.

---

## 📌 Notas

- **Seguridad:**  
  La configuración se guarda en `terraria_config.json` con permisos restringidos (chmod 600) para proteger tus credenciales.

- **Colaboración:**  
  Este proyecto está en desarrollo. Todas las contribuciones son bienvenidas. Si encuentras algún inconveniente, por favor, abre un issue.

- **Mantenimiento:**  
  El script incluye un monitor que guarda el mundo automáticamente cada 5 minutos para asegurar la integridad del progreso.
