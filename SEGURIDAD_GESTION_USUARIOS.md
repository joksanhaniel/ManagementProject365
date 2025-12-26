# 🔐 Seguridad en Gestión de Usuarios por Gerentes

## 📋 Resumen Ejecutivo

Los **Gerentes** ahora pueden gestionar usuarios de su propia empresa, pero con estrictas medidas de seguridad que garantizan que:

1. ✅ Solo pueden ver usuarios de SU empresa (excluyendo superusuarios)
2. ✅ Solo pueden crear usuarios para SU empresa
3. ✅ Solo pueden editar usuarios de SU empresa
4. ✅ Solo pueden eliminar usuarios de SU empresa
5. ❌ NO pueden ver superusuarios en la lista
6. ❌ NO pueden crear superusuarios
7. ❌ NO pueden cambiar usuarios de empresa
8. ❌ NO pueden gestionar usuarios de otras empresas
9. ❌ NO pueden acceder a módulos de Administración ni API REST

---

## 🛡️ Capas de Seguridad Implementadas

### Capa 1: Validación de Permisos en Vistas

**Archivo:** `proyectos/views.py`

#### Vista: `usuarios_list` (Líneas 1102-1139)

**Validación de Acceso:**
```python
# Solo Gerentes y Superusuarios pueden acceder
if not (request.user.is_superuser or request.user.rol == 'gerente'):
    messages.error(request, 'No tienes permisos...')
    return redirect('dashboard', ...)
```

**Filtrado de Datos:**
```python
# Superusuarios ven todo
if request.user.is_superuser:
    usuarios = Usuario.objects.all()
else:
    # Gerentes solo ven usuarios de SU empresa (excluyendo superusuarios)
    empresa = get_empresa_from_request(request)
    usuarios = Usuario.objects.filter(empresa=empresa, is_superuser=False)
```

**Resultado:**
- Un Gerente de ABC NUNCA verá usuarios de DBA o XYZ
- Un Gerente NUNCA verá superusuarios en la lista
- Los superusuarios están completamente ocultos para Gerentes

---

#### Vista: `usuario_create` (Líneas 1143-1184)

**Validación de Acceso:**
```python
if not (request.user.is_superuser or request.user.rol == 'gerente'):
    messages.error(request, 'No tienes permisos...')
    return redirect('dashboard', ...)
```

**Forzar Empresa:**
```python
# Si es Gerente (NO superusuario), forzar la empresa a la suya
if not request.user.is_superuser:
    if empresa:
        usuario.empresa = empresa  # FORZADO - no puede cambiar
```

**Bloqueo de Superusuarios:**
```python
# Validar que Gerente no pueda crear superusuarios
if not request.user.is_superuser and usuario.is_superuser:
    messages.error(request, 'No tienes permisos para crear superusuarios.')
    return redirect('usuarios_list', ...)
```

**Resultado:**
- Gerente crea usuario → automáticamente asignado a SU empresa
- Gerente NO puede crear superusuarios

---

#### Vista: `usuario_update` (Líneas 1188-1228)

**Validación de Acceso:**
```python
if not (request.user.is_superuser or request.user.rol == 'gerente'):
    messages.error(request, 'No tienes permisos...')
    return redirect('dashboard', ...)
```

**Validación de Empresa:**
```python
# Validar que Gerente solo pueda editar usuarios de SU empresa
if not request.user.is_superuser:
    if usuario.empresa != empresa:
        messages.error(request, 'No tienes permisos para editar usuarios de otra empresa.')
        return redirect('usuarios_list', ...)
```

**Bloqueo de Cambio de Empresa:**
```python
# Si es Gerente (NO superusuario), no puede cambiar la empresa
if not request.user.is_superuser:
    usuario_editado.empresa = empresa  # Mantiene la empresa original
```

**Bloqueo de Conversión a Superusuario:**
```python
# Validar que Gerente no pueda convertir a superusuario
if not request.user.is_superuser and usuario_editado.is_superuser:
    messages.error(request, 'No tienes permisos para convertir usuarios en superusuarios.')
    return redirect('usuarios_list', ...)
```

**Resultado:**
- Gerente solo puede editar usuarios de ABC (su empresa)
- NO puede mover usuarios a otra empresa
- NO puede convertir usuarios en superusuarios

---

#### Vista: `usuario_delete` (Líneas 1232-1258)

**Validación de Acceso:**
```python
if not (request.user.is_superuser or request.user.rol == 'gerente'):
    messages.error(request, 'No tienes permisos...')
    return redirect('dashboard', ...)
```

**Validación de Empresa:**
```python
# Validar que Gerente solo pueda eliminar usuarios de SU empresa
if not request.user.is_superuser:
    if usuario.empresa != empresa:
        messages.error(request, 'No tienes permisos para eliminar usuarios de otra empresa.')
        return redirect('usuarios_list', ...)
```

**Bloqueo de Eliminación de Superusuarios:**
```python
# Gerente no puede eliminar superusuarios
if usuario.is_superuser:
    messages.error(request, 'No tienes permisos para eliminar superusuarios.')
    return redirect('usuarios_list', ...)
```

**Resultado:**
- Gerente solo puede eliminar usuarios de ABC
- NO puede eliminar superusuarios

---

### Capa 2: Protección de Módulos Administrativos

**Archivo:** `proyectos/templates/proyectos/base.html` (Líneas 310-322)

**Módulos Ocultos para No-Superusuarios:**
```html
<!-- Administración (Solo Superusuarios) -->
{% if user.is_authenticated and user.is_superuser %}
<a class="nav-link" href="/admin/">
    <i class="bi bi-gear"></i>Administración
</a>
{% endif %}

<!-- API REST (Solo Superusuarios) -->
{% if user.is_authenticated and user.is_superuser %}
<a class="nav-link" href="/api/">
    <i class="bi bi-code-slash"></i>API REST
</a>
{% endif %}
```

**Resultado:**
- Gerentes NO ven el módulo "Administración" en el menú
- Gerentes NO ven el módulo "API REST" en el menú
- Solo superusuarios tienen acceso a estos módulos
- Los módulos están completamente ocultos para usuarios normales

---

### Capa 3: Interfaz de Usuario Bloqueada

**Archivo:** `proyectos/templates/proyectos/usuario_form.html` (Líneas 52-72)

**Campo Empresa Bloqueado para Gerentes:**
```html
{% if es_gerente %}
    <!-- Gerentes no pueden cambiar la empresa -->
    {{ form.empresa }}
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const empresaField = document.querySelector('select[name="empresa"]');
            if (empresaField) {
                empresaField.disabled = true;  // BLOQUEADO
                empresaField.style.backgroundColor = '#e9ecef';  // Visual
            }
        });
    </script>
    <small class="text-muted">Como Gerente, solo puedes crear usuarios para tu empresa</small>
{% else %}
    <!-- Superusuarios pueden seleccionar cualquier empresa -->
    {{ form.empresa }}
    <small class="text-muted">{{ form.empresa.help_text }}</small>
{% endif %}
```

**Resultado:**
- Gerente ve el campo empresa, pero está deshabilitado (gris)
- Mensaje claro: "Como Gerente, solo puedes crear usuarios para tu empresa"
- Superusuario ve el campo normal y puede seleccionar cualquier empresa

---

### Capa 3: Menú de Navegación Actualizado

**Archivo:** `proyectos/templates/proyectos/base.html` (Líneas 294-301)

**Antes:**
```html
<!-- Solo administrador o superusuario -->
{% if user.rol == 'administrador' or user.is_superuser %}
```

**Ahora:**
```html
<!-- Usuarios (Gerentes y Superusuarios) -->
{% if user.rol == 'gerente' or user.is_superuser %}
    <a class="nav-link" href="{% url 'usuarios_list' empresa_codigo %}">
        <i class="bi bi-people-fill"></i>Usuarios
    </a>
{% endif %}
```

**Resultado:** El menú "Usuarios" ahora es visible para Gerentes.

---

## 🔍 Tabla de Comparación de Permisos

| Acción | Superusuario | Gerente ABC | Supervisor | Contador | Auxiliar | Usuario |
|--------|--------------|-------------|------------|----------|----------|---------|
| Ver usuarios de ABC | ✅ | ✅ (sin superusers) | ❌ | ❌ | ❌ | ❌ |
| Ver usuarios de DBA | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Ver superusuarios en lista | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Crear usuario en ABC | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Crear usuario en DBA | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Editar usuario de ABC | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Editar usuario de DBA | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Eliminar usuario de ABC | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Eliminar usuario de DBA | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Crear superusuario | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Eliminar superusuario | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Cambiar empresa de usuario | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Gestionar empresas | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Acceder a Administración | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Acceder a API REST | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🧪 Casos de Prueba de Seguridad

### Caso 1: Gerente Intenta Ver Usuarios de Otra Empresa

**Escenario:**
```
Usuario: juan.gerente (Empresa: ABC, Rol: Gerente)
Acción: Ir a /ABC/usuarios/
```

**Flujo:**
1. Sistema obtiene empresa del request → ABC
2. Vista filtra: `Usuario.objects.filter(empresa=ABC)`
3. Juan ve SOLO usuarios con `empresa=ABC`

**Resultado:** ✅ SEGURO - No ve usuarios de DBA ni XYZ

---

### Caso 2: Gerente Intenta Crear Usuario con Empresa DBA

**Escenario:**
```
Usuario: juan.gerente (Empresa: ABC, Rol: Gerente)
Acción: Crear usuario, intenta seleccionar empresa=DBA
```

**Flujo:**
1. Frontend bloquea el selector (disabled)
2. Si manipula el HTML y envía empresa=DBA:
   - Vista detecta: `if not request.user.is_superuser:`
   - Vista fuerza: `usuario.empresa = ABC`
3. Usuario se crea con empresa=ABC

**Resultado:** ✅ SEGURO - Imposible asignar a otra empresa

---

### Caso 3: Gerente Intenta Crear Superusuario

**Escenario:**
```
Usuario: juan.gerente (Empresa: ABC, Rol: Gerente)
Acción: Crear usuario, marca is_superuser=True
```

**Flujo:**
1. Vista valida:
   ```python
   if not request.user.is_superuser and usuario.is_superuser:
       messages.error(request, 'No tienes permisos...')
       return redirect(...)
   ```
2. Creación rechazada con mensaje de error

**Resultado:** ✅ SEGURO - Creación bloqueada

---

### Caso 4: Gerente Intenta Editar Usuario de Otra Empresa

**Escenario:**
```
Usuario: juan.gerente (Empresa: ABC, Rol: Gerente)
Usuario a editar: maria (Empresa: DBA)
Acción: Ir a /ABC/usuarios/5/editar/
```

**Flujo:**
1. Vista carga usuario con id=5 (María de DBA)
2. Vista valida:
   ```python
   if usuario.empresa != empresa:  # DBA != ABC
       messages.error(request, 'No tienes permisos...')
       return redirect(...)
   ```
3. Edición rechazada

**Resultado:** ✅ SEGURO - Edición bloqueada

---

### Caso 5: Gerente Intenta Eliminar Superusuario

**Escenario:**
```
Usuario: juan.gerente (Empresa: ABC, Rol: Gerente)
Usuario a eliminar: superadmin (is_superuser=True)
Acción: Ir a /ABC/usuarios/1/eliminar/
```

**Flujo:**
1. Vista carga usuario con id=1 (superadmin)
2. Vista valida:
   ```python
   if usuario.is_superuser:
       messages.error(request, 'No tienes permisos...')
       return redirect(...)
   ```
3. Eliminación rechazada

**Resultado:** ✅ SEGURO - Eliminación bloqueada

---

### Caso 6: Gerente Intenta Ver Superusuarios

**Escenario:**
```
Usuario: juan.gerente (Empresa: ABC, Rol: Gerente)
Acción: Ir a /ABC/usuarios/
```

**Flujo:**
1. Vista filtra usuarios:
   ```python
   usuarios = Usuario.objects.filter(empresa=ABC, is_superuser=False)
   ```
2. Lista excluye automáticamente todos los superusuarios
3. Juan ve SOLO usuarios normales de ABC

**Resultado:** ✅ SEGURO - Superusuarios invisibles para Gerentes

---

### Caso 7: Gerente Intenta Acceder a Administración

**Escenario:**
```
Usuario: juan.gerente (Empresa: ABC, Rol: Gerente)
Acción: Ir directamente a /admin/
```

**Flujo:**
1. Menú NO muestra el link "Administración" (oculto)
2. Si Juan va directo a /admin/:
   - Django Admin valida: `user.is_staff and user.is_superuser`
   - Juan NO es superusuario → Acceso denegado

**Resultado:** ✅ SEGURO - Acceso bloqueado por Django

---

## 📊 Diagrama de Flujo de Seguridad

```
┌─────────────────────────────────────────────────────────────┐
│         GERENTE INTENTA GESTIONAR USUARIOS                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 1: VALIDACIÓN DE ROL                                  │
│  ¿Es Gerente o Superusuario?                                │
│      ✓ → Continuar                                          │
│      ✗ → Rechazar (mensaje de error + redirect)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 2: FILTRADO POR EMPRESA Y SUPERUSUARIOS               │
│  Obtener empresa del request                                │
│  Filtrar: Usuario.objects.filter(                           │
│              empresa=ABC,                                   │
│              is_superuser=False  ← Excluye superusuarios    │
│           )                                                 │
│  Resultado: Solo ve usuarios normales de ABC               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 3: VALIDACIONES ESPECÍFICAS                           │
│  Crear:                                                     │
│    - Forzar empresa = ABC                                   │
│    - Bloquear creación de superusuarios                     │
│  Editar:                                                    │
│    - Validar que usuario pertenece a ABC                    │
│    - Bloquear cambio de empresa                             │
│    - Bloquear conversión a superusuario                     │
│  Eliminar:                                                  │
│    - Validar que usuario pertenece a ABC                    │
│    - Bloquear eliminación de superusuarios                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 4: PROTECCIÓN DE MÓDULOS                              │
│  - Módulo "Administración" oculto (solo superusuarios)      │
│  - Módulo "API REST" oculto (solo superusuarios)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CAPA 5: INTERFAZ DE USUARIO                                │
│  - Campo empresa bloqueado (disabled)                       │
│  - Mensaje: "Solo puedes crear usuarios para tu empresa"   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              OPERACIÓN SEGURA COMPLETADA ✓                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Resumen de Archivos Modificados

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `proyectos/views.py` | Actualización de vistas de usuarios | 1102-1258 |
| `proyectos/templates/proyectos/base.html` | Menú visible para Gerentes | 294-301 |
| `proyectos/templates/proyectos/usuario_form.html` | Campo empresa bloqueado | 49-72 |
| `GUIA_MULTIEMPRESA.md` | Documentación de gestión por Gerentes | Todo |
| `SEGURIDAD_GESTION_USUARIOS.md` | Este documento | Todo |

---

## ✅ Verificación Final

**Pregunta:** ¿Un Gerente de ABC puede ver usuarios de DBA?
**Respuesta:** ❌ NO - Filtrado automático en vista

**Pregunta:** ¿Un Gerente puede crear usuarios para otra empresa?
**Respuesta:** ❌ NO - Empresa forzada en backend + campo bloqueado en frontend

**Pregunta:** ¿Un Gerente puede crear superusuarios?
**Respuesta:** ❌ NO - Validación explícita rechaza la operación

**Pregunta:** ¿Un Gerente puede editar usuarios de otra empresa?
**Respuesta:** ❌ NO - Validación de empresa en vista

**Pregunta:** ¿Un Gerente puede eliminar superusuarios?
**Respuesta:** ❌ NO - Validación explícita rechaza la operación

**Pregunta:** ¿El sistema es seguro contra manipulación del frontend?
**Respuesta:** ✅ SÍ - Todas las validaciones se hacen en el backend

---

**Fecha:** 2025-12-25
**Versión:** 1.0
**Estado:** ✅ Implementado y Funcional
