# MultiProject Pro

Sistema completo de gestión multiempresa para proyectos y nómina desarrollado en Django 5.0 con SQL Server.

## 🏗️ Características

- **Gestión de Proyectos**: Crear, editar y dar seguimiento a proyectos
  - Tracking de pagos del cliente (desembolsos parciales)
  - Órdenes de cambio para trabajos adicionales
  - Cálculo automático de monto total del proyecto
- **Gestión de Empleados**: Administrar personal y asignaciones a proyectos
  - Historial de cambios salariales
  - Tracking de préstamos y anticipos
- **Planillas de Pago**: Sistema flexible de nómina (semanal, quincenal, mensual)
  - Deducciones detalladas (IHSS, ISR, préstamos, anticipos, etc.)
  - Control manual de deducciones (no automático)
  - Historial completo de deducciones por empleado
  - Semana laboral de 6 días (lunes a sábado)
- **Control de Gastos**: Registro y seguimiento de gastos por proyecto
- **Gestión de Proveedores**: Administrar proveedores y sus datos
- **Sistema de Usuarios con Roles**: 5 roles diferentes con permisos granulares
- **Reportes y Dashboard**: Visualización de métricas clave
- **Diseño Responsive**: Adaptado a dispositivos móviles y tablets

## 🎭 Roles del Sistema

1. **Administrador**: Acceso total + gestión de usuarios
2. **Gerente de Proyecto**: Gestión completa de proyectos y finanzas
3. **Contador**: Acceso financiero, planillas y gastos
4. **Supervisor de Obra**: Gestión de empleados y asignaciones
5. **Consultor**: Solo lectura de proyectos y reportes

## 🚀 Instalación

### Prerrequisitos

- Python 3.11+
- SQL Server 2019+ (o SQL Server Express)
- ODBC Driver 17 for SQL Server

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd AZERHOME
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus configuraciones
# IMPORTANTE: Usar credenciales seguras
```

5. **Configurar base de datos**
- Crear base de datos en SQL Server:
```sql
CREATE DATABASE MPP365DB;
```

6. **Aplicar migraciones**
```bash
python manage.py migrate
```

7. **Crear superusuario**
```bash
python create_superuser.py
```
El script solicitará usuario, email y contraseña segura.

8. **Iniciar servidor**
```bash
python manage.py runserver
```

9. **Acceder al sistema**
- URL: http://localhost:8000/
- Admin: http://localhost:8000/admin/

## 🔒 Seguridad

**⚠️ IMPORTANTE**: Este sistema maneja información sensible.

### Antes de Usar en Producción:

1. **Leer la guía de seguridad**: [SEGURIDAD.md](SEGURIDAD.md)
2. **Generar nueva SECRET_KEY**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
3. **Configurar `DEBUG=False`** en producción
4. **Usar HTTPS** en producción
5. **Configurar contraseñas fuertes** para todos los usuarios
6. **Revisar configuraciones** de seguridad en settings.py

### Configuraciones de Seguridad Implementadas:

- ✅ Validación robusta de contraseñas (mínimo 8 caracteres)
- ✅ Sesiones con timeout (30 minutos de inactividad)
- ✅ Protección CSRF y XSS
- ✅ Headers de seguridad configurados
- ✅ Control de acceso basado en roles
- ✅ Variables de entorno para credenciales

## 📁 Estructura del Proyecto

```
MPP365/
├── mpp365_system/     # Configuración principal
│   ├── settings.py         # Configuraciones
│   ├── urls.py            # URLs principales
│   └── wsgi.py
├── proyectos/              # App principal
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas
│   ├── forms.py           # Formularios
│   ├── decorators.py      # Control de acceso
│   ├── admin.py           # Admin de Django
│   └── templates/         # Templates HTML
├── .env.example           # Ejemplo de configuración
├── .gitignore            # Archivos a ignorar
├── requirements.txt       # Dependencias
├── manage.py             # Comando Django
├── reset_db.py           # Script reset BD
├── create_superuser.py   # Script crear admin
├── README.md             # Este archivo
├── SEGURIDAD.md          # Guía de seguridad
└── SISTEMA_USUARIOS_Y_ROLES.md  # Doc de roles
```

## 📚 Documentación

- **[SEGURIDAD.md](SEGURIDAD.md)**: Guía completa de seguridad
- **[SISTEMA_USUARIOS_Y_ROLES.md](SISTEMA_USUARIOS_Y_ROLES.md)**: Matriz de permisos y roles
- **[SISTEMA_COMPLETADO.md](SISTEMA_COMPLETADO.md)**: Documentación técnica completa
- **[SISTEMA_DEDUCCIONES.md](SISTEMA_DEDUCCIONES.md)**: Sistema de deducciones y planillas
- **[INSTRUCCIONES_RESETEAR_BD.md](INSTRUCCIONES_RESETEAR_BD.md)**: Cómo resetear la base de datos

## 🛠️ Comandos Útiles

```bash
# Desarrollo
python manage.py runserver          # Iniciar servidor
python manage.py makemigrations     # Crear migraciones
python manage.py migrate            # Aplicar migraciones
python manage.py shell              # Shell de Django

# Gestión de Usuarios
python create_superuser.py          # Crear admin
python manage.py changepassword usuario  # Cambiar contraseña

# Base de Datos
python reset_db.py --force         # Resetear BD (¡cuidado!)
python manage.py dbshell           # Acceder a SQL

# Seguridad
python manage.py check --deploy   # Verificar config producción
```

## 🔍 Verificar Instalación

### Pruebas Básicas:

1. **Login como administrador**
2. **Crear usuario de prueba** con rol diferente
3. **Verificar permisos** según rol
4. **Probar filtros** en todos los módulos
5. **Verificar responsive** en móvil

## 📊 Módulos del Sistema

| Módulo | Descripción | Permisos |
|--------|-------------|----------|
| Dashboard | Vista general del sistema | Todos |
| Usuarios | Gestión de usuarios | Solo Admin |
| Proyectos | Proyectos de construcción | Según rol |
| Empleados | Personal de la empresa | Según rol |
| Planillas | Nóminas de pago | Financiero |
| Gastos | Control de gastos | Financiero |
| Proveedores | Gestión de proveedores | Todos (lectura) |
| Clientes | Gestión de clientes | Todos (lectura) |

## 🐛 Solución de Problemas

### Error: "No such table: proyectos_usuario"
```bash
python manage.py migrate
```

### Error: "CSRF verification failed"
- Verificar que el dominio esté en ALLOWED_HOSTS
- Verificar configuraciones de cookies en settings.py

### Error: "Permission denied"
- Verificar que el usuario tenga el rol correcto
- Revisar decoradores en las vistas

### No aparece opción "Usuarios" en menú
- Solo visible para administradores
- Verificar campo `rol` del usuario

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/NuevaFuncionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/NuevaFuncionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es privado y confidencial.

## 👥 Contacto

Para soporte o consultas sobre el sistema, contactar al administrador.

---

## ⚠️ Recordatorios de Seguridad

- 🔒 **NUNCA** subir el archivo `.env` al repositorio
- 🔒 **NUNCA** usar contraseñas por defecto en producción
- 🔒 **SIEMPRE** usar HTTPS en producción
- 🔒 **REVISAR** la guía [SEGURIDAD.md](SEGURIDAD.md) antes de desplegar

---

**Versión**: 1.0
**Framework**: Django 5.0
**Base de Datos**: SQL Server
**Última Actualización**: Diciembre 2025
