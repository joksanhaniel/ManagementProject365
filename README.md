# MPP365 - MultiProject Pro

Sistema de gestión integral para empresas constructoras desarrollado con Django 4.2.17 LTS y PostgreSQL 16.

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Características Principales](#características-principales)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Sistema de Roles y Permisos](#sistema-de-roles-y-permisos)
6. [Módulos del Sistema](#módulos-del-sistema)
7. [Arquitectura Multiempresa](#arquitectura-multiempresa)
8. [Gestión de Maquinaria](#gestión-de-maquinaria)
9. [API REST](#api-rest)
10. [Base de Datos](#base-de-datos)
11. [Seguridad](#seguridad)
12. [Comandos Útiles](#comandos-útiles)
13. [Solución de Problemas](#solución-de-problemas)

---

## 📖 Descripción General

**MPP365 (MultiProject Pro)** es un sistema completo de gestión empresarial diseñado específicamente para empresas constructoras. Permite administrar múltiples proyectos, empleados, planillas, gastos, maquinaria y más, todo en un solo lugar.

### Características Destacadas

- ✅ **Multiempresa**: Gestiona múltiples empresas desde una sola instalación
- ✅ **Sistema de Roles**: 7 roles diferentes con permisos granulares
- ✅ **Gestión de Proyectos**: Control completo de proyectos de construcción
- ✅ **Planillas de Pago**: Cálculo automático de salarios, deducciones y bonificaciones
- ✅ **Control de Gastos**: Registro y seguimiento de gastos con archivos adjuntos
- ✅ **Gestión de Maquinaria**: Control de equipos, tarifas y uso
- ✅ **Reportes Financieros**: Análisis detallado de costos y rentabilidad
- ✅ **API REST**: Integración con otros sistemas
- ✅ **Responsive**: Funciona en dispositivos móviles, tablets y escritorio

---

## 🚀 Características Principales

### 1. Gestión de Proyectos
- Crear y administrar múltiples proyectos
- Asignar empleados a proyectos
- Seguimiento de presupuesto vs gastos reales
- Órdenes de cambio con aprobaciones
- Estados de proyecto (planificación, ejecución, completado, etc.)

### 2. Gestión de Recursos Humanos
- Registro completo de empleados
- Control de asistencias
- Tipos de contrato (permanente, temporal, por proyecto)
- Historial de salarios
- Asignación de empleados a proyectos

### 3. Planillas de Pago
- Cálculo automático de salarios
- Gestión de deducciones (ISR, seguro social, préstamos)
- Bonificaciones y horas extra
- Generación de reportes de planilla
- Registro de pagos individuales

### 4. Control de Gastos
- Registro de gastos por proyecto
- Clasificación por categorías
- Carga de archivos adjuntos (facturas, recibos)
- Reportes de gastos por proyecto
- Control presupuestario

### 5. Gestión de Maquinaria
- Inventario de maquinaria y equipos
- Control de tarifas por hora
- Historial de cambios de tarifa
- Estados: disponible, en uso, mantenimiento, fuera de servicio
- Registro de uso de maquinaria
- Asignación de operadores
- Control de horómetros

### 6. Clientes y Proveedores
- Gestión de clientes
- Gestión de proveedores
- Información de contacto completa
- Historial de proyectos/compras

### 7. Reportes y Analytics
- Dashboard con indicadores clave
- Reportes financieros por proyecto
- Análisis de rentabilidad
- Costos laborales y de maquinaria
- Exportación de datos

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 4.2.17 LTS** - Framework web principal
- **Python 3.11** - Lenguaje de programación
- **PostgreSQL 16** - Base de datos relacional
- **Django REST Framework** - API REST
- **python-decouple** - Gestión de configuración

### Frontend
- **Bootstrap 5.3** - Framework CSS
- **Bootstrap Icons** - Iconografía
- **JavaScript ES6+** - Interactividad
- **Select2** - Dropdowns mejorados (opcional)

### Dependencias Principales
```
Django==4.2.17
psycopg2-binary==2.9.11
djangorestframework==3.14.0
python-decouple==3.8
Pillow==10.0.0
```

---

## 📦 Instalación y Configuración

### Requisitos Previos

1. **Python 3.11+**
2. **PostgreSQL 16+**
3. **Git** (opcional)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/mpp365.git
cd mpp365
```

### Paso 2: Crear Entorno Virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar PostgreSQL

**Crear base de datos**:

```bash
# Opción 1: Usando Python
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', user='postgres', password='tu_password', dbname='postgres'); conn.autocommit = True; cur = conn.cursor(); cur.execute('CREATE DATABASE mpp365'); cur.close(); conn.close()"

# Opción 2: Usando psql
psql -U postgres -c "CREATE DATABASE mpp365;"
```

### Paso 5: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Database Configuration - PostgreSQL
DB_NAME=mpp365
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Security
SECRET_KEY=tu_secret_key_aqui
DEBUG=True

# Allowed Hosts (separados por coma)
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Paso 6: Ejecutar Migraciones

```bash
python manage.py migrate
```

### Paso 7: Crear Superusuario

```bash
python manage.py createsuperuser
```

### Paso 8: Iniciar Servidor

```bash
python manage.py runserver
```

Acceder a: **http://localhost:8000/DEFAULT/**

---

## 👥 Sistema de Roles y Permisos

El sistema cuenta con **7 roles** diferentes con permisos específicos:

### 1. 🌟 Superusuario

**Uso**: Administrador del sistema (solo tú)

**Permisos**:
- Acceso total al sistema
- Gestión de empresas (multiempresa)
- Gestión de usuarios de todas las empresas
- Acceso al panel de administración Django
- Puede cambiar entre empresas

**Módulos**: Dashboard, Clientes, Proveedores, Empleados, Proyectos, Planillas, Gastos, Maquinaria, Usos de Maquinaria, Usuarios, Empresas, Administración, API REST

### 2. 👔 Gerente

**Uso**: Gerente general de la constructora

**Permisos**:
- Acceso total a la aplicación web (sin Django Admin)
- Gestión de usuarios de su empresa
- Crear/editar/eliminar proyectos
- Gestionar empleados, asignaciones, planillas y gastos
- Acceso completo a información financiera

**Módulos**: Dashboard, Clientes, Proveedores, Empleados, Proyectos, Planillas, Gastos, Maquinaria, Usos de Maquinaria, Usuarios

### 3. 👷 Supervisor

**Uso**: Supervisores de proyectos

**Permisos**:
- Gestión de proyectos
- Gestionar empleados y asignaciones
- Gestionar planillas y gastos
- Acceso a información financiera
- Registro de asistencias

**Módulos**: Dashboard, Clientes, Proveedores, Empleados, Proyectos, Planillas, Gastos

### 4. 💰 Contador

**Uso**: Personal de contabilidad

**Permisos**:
- Acceso a información financiera
- Gestionar planillas de pago
- Gestionar gastos del proyecto
- Generar reportes financieros
- Consultar proyectos (solo lectura)

**Módulos**: Dashboard, Proyectos (lectura), Planillas, Gastos

### 5. 🔧 Auxiliar

**Uso**: Auxiliares administrativos

**Permisos**:
- Gestión de asignaciones de empleados
- Consultar información de proyectos
- Registro de asistencias
- Sin acceso a información financiera

**Módulos**: Dashboard, Empleados, Proyectos (lectura)

### 6. 🚜 Operador

**Uso**: Operadores de maquinaria y equipo

**Permisos**:
- Gestionar gastos del proyecto
- Gestionar maquinaria y equipo
- Registrar uso de maquinaria
- Puede ser asignado como operador en usos
- **NO puede editar/eliminar usos finalizados** (solo admin)
- Sin acceso a información financiera ni planillas

**Módulos**: Dashboard, Gastos, Maquinaria, Usos de Maquinaria

### 7. 👤 Usuario

**Uso**: Consulta y visualización de reportes

**Permisos**:
- Solo lectura de proyectos
- Consultar reportes básicos
- Sin permisos de escritura
- Sin acceso a información financiera

**Módulos**: Dashboard, Proyectos (solo lectura)

### Matriz de Permisos

| Funcionalidad                     | Superusuario | Gerente | Supervisor | Contador | Auxiliar | Operador | Usuario |
|----------------------------------|:------------:|:-------:|:----------:|:--------:|:--------:|:--------:|:-------:|
| Acceso Django Admin              | ✅           | ❌      | ❌         | ❌       | ❌       | ❌       | ❌      |
| Crear/Editar Proyectos           | ✅           | ✅      | ✅         | ❌       | ❌       | ❌       | ❌      |
| Ver Proyectos                    | ✅           | ✅      | ✅         | ✅       | ✅       | ❌       | ✅      |
| Crear/Editar Empleados           | ✅           | ✅      | ✅         | ❌       | ✅       | ❌       | ❌      |
| Ver Información Financiera       | ✅           | ✅      | ✅         | ✅       | ❌       | ❌       | ❌      |
| Gestionar Planillas              | ✅           | ✅      | ✅         | ✅       | ❌       | ❌       | ❌      |
| Gestionar Gastos                 | ✅           | ✅      | ✅         | ✅       | ❌       | ✅       | ❌      |
| Gestionar Maquinaria             | ✅           | ✅      | ❌         | ❌       | ❌       | ✅       | ❌      |
| Gestionar Usos de Maquinaria     | ✅           | ✅      | ❌         | ❌       | ❌       | ✅*      | ❌      |
| Editar Usos Finalizados          | ✅           | ❌      | ❌         | ❌       | ❌       | ❌       | ❌      |
| Ver Reportes                     | ✅           | ✅      | ✅         | ✅       | ✅       | ❌       | ✅      |
| Gestionar Usuarios               | ✅           | ✅**    | ❌         | ❌       | ❌       | ❌       | ❌      |

**Notas**:
- (*) Los operadores pueden crear y editar usos de maquinaria activos, pero solo los administradores pueden editar/eliminar usos finalizados.
- (**) Los gerentes solo pueden gestionar usuarios de su propia empresa.

### Crear Usuarios por Rol

#### Crear Gerente
```python
from proyectos.models import Usuario, Empresa

empresa = Empresa.objects.get(codigo='DEFAULT')

gerente = Usuario.objects.create_user(
    username='juan.perez',
    email='juan.perez@empresa.com',
    first_name='Juan',
    last_name='Pérez',
    password='contraseña_segura',
    rol='gerente',
    empresa=empresa,
    is_staff=False
)
```

#### Crear Operador
```python
operador = Usuario.objects.create_user(
    username='pedro.ramirez',
    email='pedro.ramirez@empresa.com',
    first_name='Pedro',
    last_name='Ramírez',
    password='contraseña_segura',
    rol='operador',
    empresa=empresa,
    is_staff=False
)
```

---

## 📊 Módulos del Sistema

### 1. Dashboard
- Resumen de proyectos activos
- Indicadores clave de rendimiento (KPIs)
- Alertas y notificaciones
- Accesos rápidos

### 2. Proyectos
- Crear y gestionar proyectos
- Asignar empleados
- Control presupuestario
- Órdenes de cambio
- Reportes de avance

### 3. Empleados
- Registro de empleados
- Tipos de contrato
- Asignaciones a proyectos
- Historial laboral

### 4. Planillas de Pago
- Generación de planillas
- Cálculo de deducciones
- Bonificaciones y horas extra
- Registro de pagos
- Reportes mensuales

### 5. Gastos
- Registro de gastos por proyecto
- Carga de archivos adjuntos
- Categorización
- Reportes y análisis

### 6. Maquinaria
- Inventario de equipos
- Control de tarifas
- Historial de cambios
- Estados de maquinaria

### 7. Usos de Maquinaria
- Registro de uso
- Asignación de operadores
- Control de horómetros
- Cálculo automático de costos
- Filtros por estado (activo/finalizado)

### 8. Clientes
- Gestión de clientes
- Información de contacto
- Historial de proyectos

### 9. Proveedores
- Gestión de proveedores
- Datos de contacto
- Historial de compras

### 10. Usuarios
- Gestión de usuarios
- Asignación de roles
- Control de accesos
- Información de roles

---

## 🏢 Arquitectura Multiempresa

El sistema soporta múltiples empresas independientes desde una sola instalación.

### Características

- **Aislamiento de Datos**: Cada empresa solo ve sus propios datos
- **URL por Empresa**: `http://localhost:8000/{CODIGO_EMPRESA}/`
- **Gestión Centralizada**: Superusuarios pueden gestionar todas las empresas
- **Usuarios por Empresa**: Cada usuario pertenece a una empresa específica

### Estructura de URLs

```
/{empresa_codigo}/                       # Dashboard
/{empresa_codigo}/proyectos/            # Lista de proyectos
/{empresa_codigo}/empleados/            # Lista de empleados
/{empresa_codigo}/planillas/            # Planillas de pago
/{empresa_codigo}/gastos/               # Gastos
/{empresa_codigo}/maquinarias/          # Maquinaria
/{empresa_codigo}/usos-maquinaria/      # Usos de maquinaria
/{empresa_codigo}/usuarios/             # Gestión de usuarios
```

### Middleware de Empresa

El sistema usa un middleware (`EmpresaMiddleware`) que:
1. Extrae el código de empresa de la URL
2. Valida que la empresa existe
3. Asigna la empresa al request
4. Filtra automáticamente los datos por empresa

---

## 🚜 Gestión de Maquinaria

### Características Principales

#### 1. Inventario de Maquinaria
- Código único por equipo
- Nombre descriptivo
- Tipo de maquinaria
- Marca y modelo
- Tarifa por hora
- Horómetro inicial
- Estados: disponible, en uso, mantenimiento, fuera de servicio

#### 2. Control de Tarifas
- Historial completo de cambios de tarifa
- Fecha y hora de cada cambio
- Tarifa anterior y nueva
- Usuario que realizó el cambio
- Motivo del cambio

#### 3. Registro de Uso
- Asignación a proyectos
- Operador asignado (usuario con rol operador)
- Fecha y hora de inicio
- Horómetro inicial
- Fecha y hora de finalización (opcional)
- Horómetro final (opcional)
- Tarifa aplicada
- Descripción del trabajo realizado
- Observaciones

#### 4. Cálculo Automático de Costos
- Cálculo de horas trabajadas
- Aplicación de tarifa vigente
- Actualización automática del horómetro
- Costos por uso

#### 5. Control de Usos Finalizados
- Los usos con `fecha_fin` y `horometro_final` se consideran **finalizados**
- Solo **superusuarios** pueden editar/eliminar usos finalizados
- Gerentes y operadores solo pueden editar usos activos
- Previene modificaciones accidentales en registros históricos

#### 6. Filtros y Reportes
- Filtro por proyecto
- Filtro por maquinaria
- Filtro por estado (activo/finalizado)
- Reportes de uso por periodo
- Análisis de costos de maquinaria

### Flujo de Trabajo

1. **Crear Maquinaria**: Admin/Gerente registra el equipo
2. **Establecer Tarifa**: Define tarifa por hora
3. **Registrar Uso**: Operador inicia uso en proyecto
4. **Asignar Operador**: Usuario con rol operador
5. **Finalizar Uso**: Registrar horómetro final y fecha
6. **Análisis**: Revisar costos y eficiencia

---

## 🔌 API REST

El sistema incluye una API RESTful completa para integración con otros sistemas.

### Endpoints Principales

#### Proyectos
```
GET    /api/proyectos/              # Listar proyectos
POST   /api/proyectos/              # Crear proyecto
GET    /api/proyectos/{id}/         # Detalle de proyecto
PUT    /api/proyectos/{id}/         # Actualizar proyecto
DELETE /api/proyectos/{id}/         # Eliminar proyecto
```

#### Empleados
```
GET    /api/empleados/              # Listar empleados
POST   /api/empleados/              # Crear empleado
GET    /api/empleados/{id}/         # Detalle de empleado
PUT    /api/empleados/{id}/         # Actualizar empleado
DELETE /api/empleados/{id}/         # Eliminar empleado
```

#### Planillas
```
GET    /api/planillas/              # Listar planillas
POST   /api/planillas/              # Crear planilla
GET    /api/planillas/{id}/         # Detalle de planilla
```

#### Gastos
```
GET    /api/gastos/                 # Listar gastos
POST   /api/gastos/                 # Crear gasto
GET    /api/gastos/{id}/            # Detalle de gasto
PUT    /api/gastos/{id}/            # Actualizar gasto
DELETE /api/gastos/{id}/            # Eliminar gasto
```

### Autenticación

La API usa autenticación basada en tokens o sesión de Django.

---

## 💾 Base de Datos

### PostgreSQL 16

El sistema utiliza PostgreSQL 16 como motor de base de datos.

#### Ventajas de PostgreSQL

1. **Open Source y Gratuito**
2. **Alto Rendimiento**
3. **ACID Completo**
4. **Características Avanzadas**: JSON, Arrays, Full-text search
5. **Escalabilidad**: MVCC, Replicación, Particionamiento
6. **Compatibilidad con Django**

#### Configuración Recomendada

**postgresql.conf**:
```conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB
```

#### Backups

**Crear backup**:
```bash
pg_dump -U postgres -d mpp365 -F c -f backup_mpp365.dump
```

**Restaurar backup**:
```bash
pg_restore -U postgres -d mpp365 backup_mpp365.dump
```

### Modelo de Datos

El sistema cuenta con los siguientes modelos principales:

- **Empresa**: Empresas del sistema
- **Usuario**: Usuarios con roles
- **Cliente**: Clientes de la empresa
- **Proveedor**: Proveedores
- **Proyecto**: Proyectos de construcción
- **Empleado**: Empleados de la empresa
- **Asignacion**: Asignación de empleados a proyectos
- **Planilla**: Planillas de pago
- **DetallePlanilla**: Detalle de pagos por empleado
- **Gasto**: Gastos de proyectos
- **Maquinaria**: Inventario de maquinaria
- **HistorialTarifaMaquinaria**: Historial de tarifas
- **UsoMaquinaria**: Registro de uso de maquinaria
- **OrdenCambio**: Órdenes de cambio de proyectos
- **Pago**: Registro de pagos
- **TipoDeduccion**: Tipos de deducciones
- **Deduccion**: Deducciones aplicadas
- **HoraExtra**: Horas extra trabajadas
- **Bonificacion**: Bonificaciones otorgadas

---

## 🔒 Seguridad

### Mejores Prácticas Implementadas

1. **Autenticación y Autorización**
   - Sistema de roles robusto
   - Permisos a nivel de vista
   - Decoradores `@login_required`
   - Verificación de permisos por rol

2. **Protección CSRF**
   - Tokens CSRF en formularios
   - Validación automática por Django

3. **Validación de Datos**
   - Validación en modelos
   - Validación en formularios
   - Sanitización de entrada

4. **SQL Injection**
   - Uso de ORM de Django
   - Consultas parametrizadas

5. **XSS Protection**
   - Escapado automático de templates
   - Django template engine

6. **Gestión de Contraseñas**
   - Hash con PBKDF2
   - Validadores de contraseña
   - Longitud mínima de 8 caracteres

7. **Archivos Adjuntos**
   - Validación de tipos de archivo
   - Límite de tamaño
   - Almacenamiento seguro

### Configuración de Seguridad

**settings.py**:
```python
# Security Settings
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Session Security
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
```

### Recomendaciones para Producción

1. **Cambiar SECRET_KEY** a un valor único y seguro
2. **DEBUG = False** en producción
3. **Configurar ALLOWED_HOSTS** correctamente
4. **Usar HTTPS** (SSL/TLS)
5. **Configurar firewall** en el servidor
6. **Backups automáticos** de la base de datos
7. **Monitorear logs** regularmente
8. **Actualizar dependencias** periódicamente
9. **Usar variables de entorno** para credenciales
10. **Implementar rate limiting** en API

---

## 🔧 Comandos Útiles

### Django

**Migraciones**:
```bash
python manage.py makemigrations        # Crear migraciones
python manage.py migrate               # Aplicar migraciones
python manage.py showmigrations        # Ver estado de migraciones
```

**Usuarios**:
```bash
python manage.py createsuperuser       # Crear superusuario
python manage.py changepassword admin  # Cambiar contraseña
```

**Shell**:
```bash
python manage.py shell                 # Abrir shell de Django
python manage.py dbshell               # Abrir shell de base de datos
```

**Servidor**:
```bash
python manage.py runserver             # Iniciar servidor de desarrollo
python manage.py runserver 0.0.0.0:8000  # Accesible desde red
```

**Otros**:
```bash
python manage.py check                 # Verificar configuración
python manage.py collectstatic         # Recopilar archivos estáticos
python manage.py test                  # Ejecutar tests
```

### PostgreSQL

**Conectar a base de datos**:
```bash
psql -U postgres -d mpp365
```

**Comandos SQL útiles**:
```sql
-- Ver tablas
\dt

-- Describir tabla
\d proyectos_proyecto

-- Ver usuarios
SELECT username, email, rol, is_active FROM proyectos_usuario;

-- Ver empresas
SELECT codigo, nombre FROM proyectos_empresa;
```

### Python Shell Examples

**Crear usuario**:
```python
from proyectos.models import Usuario, Empresa

empresa = Empresa.objects.get(codigo='DEFAULT')

usuario = Usuario.objects.create_user(
    username='juan.perez',
    email='juan.perez@empresa.com',
    first_name='Juan',
    last_name='Pérez',
    password='contraseña_segura',
    rol='gerente',
    empresa=empresa,
    is_staff=False
)
```

**Ver todos los usuarios y roles**:
```python
from proyectos.models import Usuario

for user in Usuario.objects.all():
    print(f"{user.username} - {user.get_rol_display()} - Empresa: {user.empresa.nombre if user.empresa else 'Sin empresa'}")
```

---

## 🐛 Solución de Problemas

### Error: "connection refused" (PostgreSQL)

**Causa**: PostgreSQL no está corriendo

**Solución**:
```bash
# Windows
services.msc
# Buscar "postgresql-x64-16" e iniciarlo

# Linux
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Error: "authentication failed"

**Causa**: Credenciales incorrectas en `.env`

**Solución**: Verificar que DB_USER y DB_PASSWORD coincidan con PostgreSQL

### Error: "database does not exist"

**Causa**: Base de datos no creada

**Solución**:
```python
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', user='postgres', password='admin', dbname='postgres'); conn.autocommit = True; cur = conn.cursor(); cur.execute('CREATE DATABASE mpp365'); cur.close(); conn.close()"
```

### Error: "No such table"

**Causa**: Migraciones no aplicadas

**Solución**:
```bash
python manage.py migrate
```

### Error: "Static files not found"

**Causa**: Archivos estáticos no recopilados

**Solución**:
```bash
python manage.py collectstatic
```

### Problemas de Permisos

**Causa**: Usuario sin rol asignado o rol incorrecto

**Solución**: Verificar rol del usuario en Django Admin o shell

---

## 📚 Recursos Adicionales

- **Documentación Django**: https://docs.djangoproject.com/en/4.2/
- **Documentación PostgreSQL**: https://www.postgresql.org/docs/16/
- **Bootstrap 5**: https://getbootstrap.com/docs/5.3/
- **Django REST Framework**: https://www.django-rest-framework.org/

---

## 📝 Notas Finales

### Credenciales por Defecto

**PostgreSQL**:
- Host: localhost
- Puerto: 5432
- Base de datos: mpp365
- Usuario: postgres
- Contraseña: admin (o la que configuraste)

**Django Admin**:
- URL: http://localhost:8000/admin/
- Username: admin
- Password: admin (o la que configuraste con createsuperuser)

**Aplicación Web**:
- URL: http://localhost:8000/DEFAULT/
- Username: admin
- Password: admin (misma que Django Admin)

### Empresa por Defecto

- **Código**: DEFAULT
- **Nombre**: Constructora Principal
- **RTN**: 0000000000000

### Importante

1. **Cambiar contraseñas por defecto** en producción
2. **Configurar backups automáticos**
3. **Usar HTTPS** en producción
4. **No compartir SECRET_KEY**
5. **Mantener DEBUG=False** en producción

---

## 👨‍💻 Desarrollo

**Versión**: 1.0.0
**Django**: 4.2.17 LTS
**Python**: 3.11+
**PostgreSQL**: 16
**Última actualización**: Diciembre 2025

---

## 📄 Licencia

Este proyecto es propietario. Todos los derechos reservados.

---

**¿Preguntas o problemas?** Contacta al equipo de desarrollo.
