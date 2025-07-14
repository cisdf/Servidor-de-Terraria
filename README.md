# 🚀 Servidor de Terraria en GitHub Codespaces  
**Configura un servidor de Terraria con un solo clic - ¡Sin complicaciones!**  

> ✨ **Proyecto mantenido por [Bryan GR](https://github.com/cisdf) | [☕ Invítame un café](https://ko-fi.com/brayangr)**  

---

## 🔥 ¿Por qué usar esta solución?  
✅ **Configuración en 1 minuto** - Automatizado con Python  
☁️ **Funciona en la nube** (Codespaces)   
🛡️ **Túneles seguros** con Ngrok o Playit.gg  
🤖 **Auto-backups** y guardado automático cada 5 minutos  
📢 **Notificaciones en Discord** (configurable)  
🔐 **Gestión segura** de credenciales y configuraciones  

---

## 🛠️ Instalación Paso a Paso  

### 📥 Requisitos  
- Cuenta GitHub con acceso a Codespaces   
- Para Ngrok: Token de [Ngrok](https://ngrok.com/)  
- Opcional: Webhook de Discord para notificaciones  

### ⚡ Configuración rápida  
1. **Abre el proyecto en Codespaces** (botón verde "Code" > "Codespaces")  
2. Ejecuta en la terminal:  
   ```bash
   python setup_terraria.py
   ```  
3. Elige tu túnel preferido:  
   ```diff
   + Ngrok (fácil configuración, requiere token)
   + Playit (mejor rendimiento, configuración automática)
   ```  
4. Sigue las instrucciones interactivas para completar la configuración   
5. ¡Conéctate desde Terraria con la IP proporcionada!  

---

## 🌟 Características Avanzadas  

| Función               | Descripción                          |
|-----------------------|--------------------------------------|
| 🔄 **Auto-save**      | Guarda el mundo automáticamente cada 5 minutos |
| 📁 **Gestión de mundos** | Sistema organizado con enlaces simbólicos y backups |
| 📢 **Notificaciones** | Alertas en Discord al iniciar el servidor |
| 🔐 **Seguridad**      | Credenciales encriptadas (chmod 600) |
| 🛠️ **Configuración persistente** | Guarda tus preferencias para futuras ejecuciones |
| ⏳ **Reintentos inteligentes** | Manejo robusto de fallos en descargas |

---

## 🚧 Roadmap (Próximas Features)  
- [ ] Soporte para mods (tModLoader)  
- [ ] Soporte para más servicios de tunneling  

---

## ❓ Preguntas Frecuentes  

### ¿Cómo cambio la configuración del servidor?  
Edita el archivo `terraria-server/serverconfig.txt` después de la primera ejecución.  

### ¿Dónde se guardan los mundos?  
En el directorio `worlds/` del proyecto, con backups automáticos.  

### ¿Es gratis?  
✅ **Totalmente gratis** - Los servicios de tunneling pueden tener límites gratuitos.  
Si te gusta el proyecto:  
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/brayangr)  

### ¿Cómo configuro Discord?  
Ejecuta el script nuevamente y selecciona la opción cuando se te pregunte.  

---

## 🐛 Reporte de Problemas  
Abre un [issue en GitHub](https://github.com/cisdf/terraria-codespaces/issues) con los detalles de tu error.

---
