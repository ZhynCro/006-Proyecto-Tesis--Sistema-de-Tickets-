# 🚀 Guía de Despliegue — Sistema de Tickets

Guía paso a paso para desplegar el Sistema de Tickets en **Ubuntu LTS 26** con **PostgreSQL** y **Nginx**.

**Servidor**: `192.168.0.9`

---

## Requisitos Previos

- Acceso SSH al servidor Ubuntu LTS 26
- Usuario con privilegios `sudo`
- El repositorio Git accesible (GitHub, GitLab, o transferencia directa)

---

## Paso 1 — Actualizar el Sistema e Instalar Paquetes

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib libpq-dev \
    nginx \
    git curl
```

---

## Paso 2 — Configurar PostgreSQL

```bash
# Iniciar y habilitar PostgreSQL
sudo systemctl enable --now postgresql

# Crear usuario y base de datos
sudo -u postgres psql <<EOF
CREATE USER tickets_user WITH PASSWORD 'TU_CONTRASEÑA_SEGURA_AQUI';
CREATE DATABASE tickets_db OWNER tickets_user;
ALTER ROLE tickets_user SET client_encoding TO 'utf8';
ALTER ROLE tickets_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tickets_user SET timezone TO 'America/Caracas';
GRANT ALL PRIVILEGES ON DATABASE tickets_db TO tickets_user;
\q
EOF
```

> ⚠️ **Cambia** `TU_CONTRASEÑA_SEGURA_AQUI` por una contraseña real y segura.

### Verificar conexión:

```bash
psql -U tickets_user -d tickets_db -h localhost -W
# Ingresa la contraseña. Si entras al prompt de psql, funciona.
# Escribe \q para salir
```

---

## Paso 3 — Crear Usuario del Sistema y Clonar el Proyecto

```bash
# Crear usuario de sistema para la aplicación
sudo useradd -m -s /bin/bash tickets
sudo mkdir -p /var/www/tickets/{static,media}
sudo chown -R tickets:www-data /var/www/tickets

# Cambiar al usuario tickets
sudo -u tickets -i

# Clonar el repositorio
git clone https://github.com/TU-USUARIO/006-Proyecto-Tesis--Sistema-de-Tickets-.git ~/app
cd ~/app
```

> 💡 **Alternativa sin Git**: Si el repo es privado, puedes transferir los archivos con `scp`:
> ```bash
> # Desde tu máquina Windows (PowerShell):
> scp -r . usuario@192.168.0.9:/home/tickets/app/
> ```

---

## Paso 4 — Configurar el Entorno Virtual e Instalar Dependencias

```bash
# (como usuario tickets, en ~/app)
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

---

## Paso 5 — Configurar Variables de Entorno

```bash
# Copiar plantilla
cp .env.example .env
nano .env
```

Editar con los valores reales:

```env
DJANGO_SECRET_KEY=aqui-pega-la-clave-generada
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=192.168.0.9

DB_NAME=tickets_db
DB_USER=tickets_user
DB_PASSWORD=TU_CONTRASEÑA_SEGURA_AQUI
DB_HOST=localhost
DB_PORT=5432
```

### Generar una SECRET_KEY segura:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y pégalo como valor de `DJANGO_SECRET_KEY` en el `.env`.

---

## Paso 6 — Ejecutar Migraciones y Crear Superusuario

```bash
# Aplicar migraciones (crea las tablas en PostgreSQL)
python manage.py migrate --settings=core.settings_prod

# Crear superusuario administrador
python manage.py createsuperuser --settings=core.settings_prod
```

### Si tienes datos para migrar (datadump.json):

```bash
# Asegúrate de que datadump.json está en ~/app/
python manage.py loaddata datadump.json --settings=core.settings_prod
```

---

## Paso 7 — Recoger Archivos Estáticos

```bash
# Asegúrate de que el directorio tiene los permisos correctos
sudo chown -R tickets:www-data /var/www/tickets/static/

# Recoger archivos estáticos (se copian directo a /var/www/tickets/static/)
python manage.py collectstatic --noinput --settings=core.settings_prod
```

---

## Paso 8 — Transferir Archivos Multimedia (media/)

Desde tu máquina Windows (PowerShell):

```powershell
# Transferir carpeta media al servidor
scp -r media/* usuario@192.168.0.9:/var/www/tickets/media/
```

En el servidor:

```bash
sudo chown -R tickets:www-data /var/www/tickets/media/
```

---

## Paso 9 — Verificar que Django Funciona

```bash
# Prueba rápida con el servidor de desarrollo
python manage.py runserver 0.0.0.0:8000 --settings=core.settings_prod
```

Visita `http://192.168.0.9:8000` desde otro equipo en la red. Si ves la app, todo está bien. **Detén el servidor** con `Ctrl+C`.

---

## Paso 10 — Configurar Gunicorn como Servicio

### Probar Gunicorn manualmente primero:

```bash
cd ~/app
source .venv/bin/activate
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=core.settings_prod
```

Si funciona, `Ctrl+C` y crear el servicio systemd.

### Crear directorio para el socket:

```bash
sudo mkdir -p /run/gunicorn
sudo chown tickets:www-data /run/gunicorn
```

### Crear archivo de socket:

```bash
sudo nano /etc/systemd/system/tickets.socket
```

Contenido:

```ini
[Unit]
Description=Gunicorn Socket — Sistema de Tickets

[Socket]
ListenStream=/run/gunicorn/tickets.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
```

### Crear archivo de servicio:

```bash
sudo nano /etc/systemd/system/tickets.service
```

Contenido:

```ini
[Unit]
Description=Gunicorn — Sistema de Tickets
Requires=tickets.socket
After=network.target postgresql.service

[Service]
User=tickets
Group=www-data
WorkingDirectory=/home/tickets/app
EnvironmentFile=/home/tickets/app/.env
ExecStart=/home/tickets/app/.venv/bin/gunicorn \
    core.wsgi:application \
    --bind unix:/run/gunicorn/tickets.sock \
    --workers 3 \
    --timeout 120 \
    --env DJANGO_SETTINGS_MODULE=core.settings_prod
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Habilitar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tickets.socket tickets.service

# Verificar estado
sudo systemctl status tickets
sudo systemctl status tickets.socket
```

---

## Paso 11 — Configurar Nginx

### Crear configuración del sitio:

```bash
sudo nano /etc/nginx/sites-available/tickets
```

Contenido:

```nginx
server {
    listen 80;
    server_name 192.168.0.9;

    # Archivos estáticos (CSS, JS, imágenes del tema)
    location /static/ {
        alias /var/www/tickets/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Archivos multimedia (adjuntos de tickets, tutoriales)
    location /media/ {
        alias /var/www/tickets/media/;
        expires 7d;
    }

    # Proxy a Gunicorn
    location / {
        proxy_pass http://unix:/run/gunicorn/tickets.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Límite de upload (para adjuntos de tickets y tutoriales)
        client_max_body_size 50M;
    }
}
```

### Activar el sitio y reiniciar Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/tickets /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar
sudo systemctl restart nginx
```

---

## Paso 12 — Configurar Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx HTTP'
sudo ufw enable

# Verificar reglas
sudo ufw status
```

---

## Paso 13 — Crear Directorio de Logs

```bash
sudo -u tickets mkdir -p /home/tickets/app/logs
```

---

## ✅ Verificación Final

```bash
# 1. Verificar que Gunicorn está corriendo
sudo systemctl status tickets

# 2. Verificar que el socket existe
ls -la /run/gunicorn/tickets.sock

# 3. Verificar Nginx
sudo nginx -t
curl -I http://192.168.0.9

# 4. Verificar archivos estáticos
curl -I http://192.168.0.9/static/css/dist/styles.css

# 5. Verificar conexión a PostgreSQL
sudo -u tickets /home/tickets/app/.venv/bin/python /home/tickets/app/manage.py showmigrations --settings=core.settings_prod

# 6. Ver logs en caso de errores
sudo journalctl -u tickets -f
sudo tail -f /var/log/nginx/error.log
sudo tail -f /home/tickets/app/logs/django.log
```

---

## 🔧 Comandos Útiles Post-Despliegue

```bash
# Reiniciar la aplicación después de cambios en el código
sudo systemctl restart tickets

# Actualizar el código desde Git
cd /home/tickets/app
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=core.settings_prod
python manage.py collectstatic --noinput --settings=core.settings_prod
sudo cp -r staticfiles/* /var/www/tickets/static/
sudo systemctl restart tickets

# Ver logs en tiempo real
sudo journalctl -u tickets -f

# Entrar al shell de Django
python manage.py shell --settings=core.settings_prod

# Entrar al shell de PostgreSQL
python manage.py dbshell --settings=core.settings_prod
```

---

## 📋 Checklist de Seguridad

- [ ] `DEBUG = False` confirmado
- [ ] `SECRET_KEY` nueva (no la de desarrollo)
- [ ] `.env` **NO** está en Git
- [ ] Firewall activado (UFW)
- [ ] PostgreSQL con contraseña segura
- [ ] Permisos de archivos correctos (`tickets:www-data`)
- [ ] Archivos multimedia accesibles pero no ejecutables
