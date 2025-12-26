# 🏢 Guía de Sistema Multiempresa

## 📋 Índice
1. [Cómo Funciona la Seguridad](#cómo-funciona-la-seguridad)
2. [Configuración Inicial](#configuración-inicial)
3. [Gestión de Empresas](#gestión-de-empresas)
4. [Gestión de Usuarios](#gestión-de-usuarios)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Solución de Problemas](#solución-de-problemas)

---

## 🔒 Cómo Funciona la Seguridad

### Middleware de Seguridad (`proyectos/middleware.py`)

El sistema implementa un **middleware automático** que valida el acceso de cada usuario a las empresas:

```python
# Líneas 31-40 del middleware
if request.user.is_authenticated and not request.user.is_superuser:
    if request.empresa and request.user.empresa != request.empresa:
        # El usuario intenta acceder a una empresa que NO es la suya
        # Se REDIRIGE automáticamente a SU empresa
        return redirect(f'/{request.user.empresa.get_url_prefix()}...')
```

### ✅ Validación Automática

**Para cada request HTTP:**
1. Se extrae el código de empresa de la URL: `/ABC/dashboard/` → empresa = ABC
2. Se verifica si el usuario está autenticado
3. Si el usuario NO es superusuario:
   - Se compara `usuario.empresa` con `empresa_en_url`
   - Si NO coinciden → **REDIRECCIÓN AUTOMÁTICA** a su empresa
   - Si coinciden → Acceso permitido

### 🚫 Lo que NO puede hacer un usuario normal

Si el usuario Juan pertenece a **empresa ABC**:

- ❌ No puede acceder a `/DBA/dashboard/` (será redirigido a `/ABC/dashboard/`)
- ❌ No puede acceder a `/XYZ/clientes/` (será redirigido a `/ABC/clientes/`)
- ❌ No puede ver datos de otras empresas en la API
- ❌ No puede cambiar manualmente la URL para acceder a otra empresa

### ✅ Lo que SÍ puede hacer un superusuario

- ✅ Acceder a TODAS las empresas
- ✅ Gestionar empresas (crear, editar, eliminar)
- ✅ Crear usuarios para cualquier empresa
- ✅ Cambiar entre empresas usando el selector
- ✅ Acceder al panel de Django Admin

---

## ⚙️ Configuración Inicial

### 1. Crear la Primera Empresa (Superusuario)

```bash
# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

**Acceder al sistema:**
1. Ir a: `http://localhost:8000/`
2. Login con el superusuario
3. Ir a: `http://localhost:8000/default/empresas/`
4. Crear las empresas necesarias

### 2. Estructura de Empresas

Cada empresa debe tener:
- **Código**: Identificador único en mayúsculas (ej: ABC, DBA, XYZ)
- **Nombre**: Nombre comercial (ej: Empresa ABC)
- **Razón Social**: Nombre legal completo
- **RTN**: Registro Tributario Nacional
- **Estado**: Activa/Inactiva (solo las activas son accesibles)

---

## 🏢 Gestión de Empresas

### Crear Nueva Empresa (Solo Superusuarios)

**Ubicación:** `http://localhost:8000/default/empresas/nueva/`

**Pasos:**
1. Código: `ABC` (solo mayúsculas y números, sin espacios)
2. Nombre: `Empresa ABC`
3. Razón Social: `Empresa ABC S.A. de C.V.`
4. RTN: `08011234567890`
5. Teléfono: `2234-5678`
6. Email: `info@abc.com`
7. Dirección: `Col. Palmira, Tegucigalpa`
8. Activa: ✓

**URLs Generadas:**
- Dashboard: `http://localhost:8000/ABC/dashboard/`
- Proyectos: `http://localhost:8000/ABC/proyectos/`
- Clientes: `http://localhost:8000/ABC/clientes/`
- etc.

### Editar o Eliminar Empresas

**Ubicación:** `http://localhost:8000/default/empresas/`

⚠️ **IMPORTANTE:** No se puede eliminar una empresa que tenga:
- Usuarios asignados
- Proyectos activos
- Clientes, proveedores o empleados registrados

---

## 👥 Gestión de Usuarios

### Tipos de Usuarios

| Tipo | Acceso | Empresa | Panel Admin |
|------|--------|---------|-------------|
| **Superusuario** | Todas las empresas | Opcional (puede estar en blanco) | ✅ Sí |
| **Usuario Normal** | Solo SU empresa | **Obligatorio** | ❌ No |

### Roles Disponibles para Usuarios Normales

#### 1️⃣ **Gerente** (Máximo Acceso en su Empresa)
- **Gestión de usuarios de SU empresa** (crear, editar, eliminar)
- Crear/editar/eliminar proyectos
- Gestionar empleados y asignaciones
- Gestionar planillas y gastos
- Acceso completo a información financiera
- **NO puede:** crear superusuarios, gestionar otras empresas, cambiar usuarios de empresa

#### 2️⃣ **Supervisor**
- Gestión de proyectos
- Gestionar empleados y asignaciones
- Gestionar planillas y gastos
- Acceso a información financiera

#### 3️⃣ **Contador**
- Acceso a información financiera
- Gestionar planillas de pago
- Gestionar gastos
- Generar reportes financieros
- Consultar proyectos (solo lectura)

#### 4️⃣ **Auxiliar**
- Gestión de asignaciones de empleados
- Consultar proyectos
- Registro de asistencias
- **Sin** acceso a información financiera

#### 5️⃣ **Usuario**
- Solo lectura de proyectos
- Consultar reportes básicos
- **Sin** permisos de escritura
- **Sin** acceso a información financiera

### Crear Usuario Normal

**Ubicación:** `http://localhost:8000/default/usuarios/nuevo/`

**Ejemplo: Usuario para Empresa ABC**

```
Username: juan.perez
Nombres: Juan
Apellidos: Pérez
Email: juan.perez@abc.com
Teléfono: 9999-8888
Rol: Gerente
Empresa: ABC ← ¡CRÍTICO!
Activo: ✓
Contraseña: ********
```

**Resultado:**
- Juan SOLO puede acceder a URLs de ABC
- Si intenta ir a `/DBA/dashboard/` → Redirigido a `/ABC/dashboard/`
- Solo ve datos de la empresa ABC

### Crear Superusuario Adicional

**Ubicación:** `http://localhost:8000/default/usuarios/nuevo/`

```
Username: admin2
Nombres: María
Apellidos: López
Email: maria@sistema.com
Rol: Gerente (o cualquier rol)
Empresa: (dejar en blanco)
Activo: ✓
¿Es superusuario?: ✓ (checkbox en Django Admin)
```

⚠️ **NOTA:** Para convertir un usuario en superusuario, se debe hacer desde Django Admin:
1. Ir a: `http://localhost:8000/admin/proyectos/usuario/`
2. Editar el usuario
3. Marcar "Staff status" y "Superuser status"

---

## 👥 Gestión de Usuarios por Gerentes

### ¿Puede un Gerente crear usuarios?

**SÍ**, los Gerentes pueden gestionar usuarios, pero con restricciones de seguridad:

### ✅ Lo que un Gerente SÍ puede hacer:

1. **Ver usuarios** de su empresa solamente
2. **Crear usuarios** asignados automáticamente a su empresa
3. **Editar usuarios** de su empresa (cambiar rol, activar/desactivar)
4. **Eliminar usuarios** de su empresa

### ❌ Lo que un Gerente NO puede hacer:

1. **Ver usuarios** de otras empresas
2. **Crear** superusuarios
3. **Editar** usuarios de otras empresas
4. **Eliminar** superusuarios
5. **Cambiar** la empresa de un usuario
6. **Gestionar** empresas (solo superusuarios)

### Flujo de Seguridad para Gerentes

```
Gerente de ABC intenta crear usuario:
    ↓
Vista verifica: ¿Es Gerente o Superusuario? ✓
    ↓
Gerente llena formulario:
    - Username: nuevo.usuario
    - Rol: Contador
    - Empresa: [BLOQUEADO a ABC] ← No puede cambiar
    ↓
Al guardar:
    - Sistema fuerza: usuario.empresa = ABC
    - Validación: ¿Intenta crear superusuario? ✗
    ↓
Resultado: Usuario creado en empresa ABC ✓
```

### Ejemplo Práctico: Gerente Creando Usuario

**Usuario Gerente:** `juan.gerente` (Empresa: ABC, Rol: Gerente)

**Pasos:**
1. Juan inicia sesión → `http://localhost:8000/ABC/dashboard/`
2. Ve el menú "Usuarios" (porque es Gerente)
3. Va a: `http://localhost:8000/ABC/usuarios/`
4. **Ve SOLO usuarios de ABC** (no ve usuarios de DBA ni XYZ)
5. Click en "Nuevo Usuario"
6. Llena formulario:
   ```
   Username: maria.contador
   Rol: Contador
   Empresa: ABC (campo bloqueado - no puede cambiar)
   ```
7. Al guardar:
   - Sistema valida que Juan es Gerente
   - Fuerza `empresa = ABC`
   - Crea usuario con éxito
   - María puede iniciar sesión en `http://localhost:8000/ABC/`

**Intento bloqueado:**
```
Si Juan intenta (manipulando el formulario):
    - Cambiar empresa a DBA
    - Marcar como superusuario

Sistema rechaza:
    ❌ "No tienes permisos para crear superusuarios"
    ❌ Empresa se fuerza a ABC automáticamente
```

---

## 💡 Ejemplos Prácticos

### Escenario 1: Tres Empresas

**Empresas creadas:**
- **ABC** - Empresa ABC (Tegucigalpa)
- **DBA** - Empresa DBA (San Pedro Sula)
- **XYZ** - Empresa XYZ (La Ceiba)

**Usuarios creados:**

| Usuario | Empresa | Rol | URLs Permitidas |
|---------|---------|-----|-----------------|
| `superadmin` | (ninguna) | Superusuario | Todas las empresas |
| `juan.abc` | ABC | Gerente | Solo `/ABC/*` |
| `maria.dba` | DBA | Contador | Solo `/DBA/*` |
| `pedro.xyz` | XYZ | Supervisor | Solo `/XYZ/*` |

### Escenario 2: Intento de Acceso No Autorizado

**Usuario:** `juan.abc` (Empresa: ABC)

```
1. Juan inicia sesión
2. Sistema lo redirige a: http://localhost:8000/ABC/dashboard/

3. Juan intenta ir a: http://localhost:8000/DBA/proyectos/
   ❌ Middleware detecta: usuario.empresa (ABC) ≠ url.empresa (DBA)
   ✅ Redirige automáticamente a: http://localhost:8000/ABC/proyectos/

4. Juan intenta cambiar la URL manualmente a: http://localhost:8000/XYZ/clientes/
   ❌ Middleware detecta: usuario.empresa (ABC) ≠ url.empresa (XYZ)
   ✅ Redirige automáticamente a: http://localhost:8000/ABC/clientes/
```

**Resultado:** Es **IMPOSIBLE** que Juan acceda a datos de DBA o XYZ.

### Escenario 3: Superusuario Gestionando Todo

**Usuario:** `superadmin`

```
1. Login → Puede elegir empresa inicial
2. Puede ir a: http://localhost:8000/ABC/dashboard/ ✅
3. Puede ir a: http://localhost:8000/DBA/proyectos/ ✅
4. Puede ir a: http://localhost:8000/XYZ/clientes/ ✅
5. Puede crear usuarios para ABC, DBA o XYZ
6. Puede editar empresas en: http://localhost:8000/default/empresas/
```

---

## 🛠️ Solución de Problemas

### Problema 1: Usuario No Puede Acceder a Ninguna Empresa

**Síntoma:** Usuario inicia sesión pero es redirigido al login

**Causa:** Usuario NO tiene empresa asignada

**Solución:**
1. Ir a: `http://localhost:8000/default/usuarios/` (como superusuario)
2. Editar el usuario
3. Asignar una empresa en el campo "Empresa"
4. Guardar

### Problema 2: Usuario Ve Mensaje "No Tiene Permisos"

**Síntoma:** Error al intentar crear/editar datos

**Causa:** Rol del usuario no tiene permisos suficientes

**Solución:**
1. Verificar el rol del usuario
2. Si necesita más permisos, cambiar a rol superior:
   - Usuario → Auxiliar → Contador → Supervisor → Gerente

### Problema 3: Empresa No Aparece en el Selector

**Síntoma:** Empresa no se muestra en el formulario

**Causa:** Empresa está marcada como "Inactiva"

**Solución:**
1. Ir a: `http://localhost:8000/default/empresas/`
2. Editar la empresa
3. Marcar "Activa" ✓
4. Guardar

### Problema 4: No Puedo Eliminar una Empresa

**Síntoma:** Error al intentar eliminar

**Causa:** Empresa tiene datos relacionados (usuarios, proyectos, etc.)

**Solución:**
1. Primero, reasignar o eliminar:
   - Todos los usuarios de esa empresa
   - Todos los proyectos
   - Todos los clientes, proveedores y empleados
2. Luego eliminar la empresa

### Problema 5: URLs No Funcionan Después de Crear Empresa

**Síntoma:** Error 404 en URLs de nueva empresa

**Causa:** Código de empresa incorrecto en URL

**Verificar:**
1. El código debe estar en MAYÚSCULAS en la URL
2. Ejemplo: Si el código es "ABC", la URL es `/ABC/dashboard/` (no `/abc/`)
3. El middleware convierte automáticamente a mayúsculas

---

## 📊 Flujo de Datos Multiempresa

```
┌─────────────────────────────────────────────────────────┐
│                    REQUEST HTTP                         │
│          GET /ABC/proyectos/                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              MIDDLEWARE                                 │
│  1. Extrae código de empresa: "ABC"                    │
│  2. Busca empresa en BD: Empresa.objects.get(codigo=ABC)│
│  3. Agrega al request: request.empresa = <Empresa ABC>  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         VALIDACIÓN DE ACCESO                            │
│  ¿Usuario autenticado? ✓                               │
│  ¿Es superusuario? ✗ (usuario normal)                 │
│  usuario.empresa = ABC                                 │
│  request.empresa = ABC                                 │
│  ¿Coinciden? ✓ → PERMITIR                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    VISTA                                │
│  proyectos_list(request):                              │
│      empresa = request.empresa  # ABC                  │
│      proyectos = Proyecto.objects.filter(empresa=ABC)  │
│      # Solo muestra proyectos de empresa ABC           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  TEMPLATE                               │
│  Muestra solo datos de empresa ABC                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Notas Importantes

1. **Código de Empresa:**
   - Solo mayúsculas y números
   - Sin espacios ni caracteres especiales
   - No se puede cambiar después de crear la empresa

2. **Superusuarios:**
   - Campo "Empresa" puede estar en blanco
   - Tienen acceso a todas las empresas
   - Son los únicos que pueden gestionar empresas

3. **Usuarios Normales:**
   - DEBEN tener una empresa asignada
   - Solo pueden ver datos de SU empresa
   - No pueden cambiar de empresa

4. **Seguridad:**
   - El middleware valida CADA request
   - Es imposible saltarse la validación
   - Los intentos de acceso no autorizado son redirigidos automáticamente

5. **URLs:**
   - Formato: `/{codigo_empresa}/{modulo}/`
   - Ejemplo: `/ABC/dashboard/`, `/DBA/proyectos/`
   - El código es case-insensitive (ABC = abc = Abc)

---

## 🎯 Resumen Ejecutivo

**¿Cómo asignar usuarios a empresas?**
1. Crear empresas (como superusuario)
2. Crear usuarios y seleccionar la empresa en el formulario
3. El sistema automáticamente restringe el acceso

**¿Qué pasa si un usuario intenta acceder a otra empresa?**
- El middleware lo detecta inmediatamente
- Redirige automáticamente a su empresa
- No hay forma de saltarse esta validación

**¿Los superusuarios pueden ver todas las empresas?**
- Sí, no tienen restricciones
- Pueden cambiar entre empresas libremente
- Son los únicos que pueden gestionar el sistema multiempresa

---

**Última actualización:** 2025-12-25
**Versión del sistema:** 1.0
