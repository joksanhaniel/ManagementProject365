# ℹ️ Descripción de Roles y Módulos de Acceso

## 🌟 Superusuario

**Acceso total al sistema**

- Acceso total al sistema
- Gestión de empresas (multiempresa)
- Gestión de usuarios de todas las empresas
- Acceso al panel de administración Django
- Puede cambiar entre empresas

**Módulos**: Dashboard, Clientes, Proveedores, Empleados, Proyectos, Planillas, Gastos, Usuarios, Empresas, Administración, API REST

---

## 👔 Gerente

**Acceso total a la aplicación web (sin Django Admin)**

- Acceso total a la aplicación web (sin Django Admin)
- Gestión de usuarios de su empresa
- Crear/editar/eliminar proyectos
- Gestionar empleados, asignaciones, planillas y gastos
- Acceso completo a información financiera

**Módulos**: Dashboard, Clientes, Proveedores, Empleados, Proyectos, Planillas, Gastos, Maquinaria, Usos de Maquinaria, Usuarios

---

## 👷 Supervisor

**Gestión de proyectos, empleados, planillas y gastos**

- Gestión de proyectos
- Gestionar empleados y asignaciones
- Gestionar planillas y gastos
- Acceso a información financiera
- Registro de asistencias

**Módulos**: Dashboard, Clientes, Proveedores, Empleados, Proyectos, Planillas, Gastos

---

## 💰 Contador

**Acceso a información financiera**

- Acceso a información financiera
- Gestionar planillas de pago
- Gestionar gastos del proyecto
- Generar reportes financieros
- Consultar proyectos (solo lectura)

**Módulos**: Dashboard, Proyectos (lectura), Planillas, Gastos

---

## 🔧 Auxiliar

**Gestión de asignaciones de empleados**

- Gestión de asignaciones de empleados
- Consultar información de proyectos
- Registro de asistencias
- Sin acceso a información financiera

**Módulos**: Dashboard, Empleados, Proyectos (lectura)

---

## 🚜 Operador

**Acceso a Gastos y Maquinaria**

- Puede registrar y gestionar gastos del proyecto
- Puede registrar y gestionar uso de maquinaria
- Puede ser asignado como operador en usos de maquinaria
- **NO puede editar/eliminar usos de maquinaria finalizados** (solo admin)
- Sin acceso a información financiera, planillas o empleados

**Módulos**: Dashboard, Gastos, Maquinaria, Usos de Maquinaria

---

## 👤 Usuario

**Solo lectura de proyectos**

- Solo lectura de proyectos
- Consultar reportes básicos
- Sin permisos de escritura
- Sin acceso a información financiera

**Módulos**: Dashboard, Proyectos (solo lectura)

---

## 📊 Matriz Completa de Permisos

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

---

## 🔑 Notas Importantes

### Superusuario vs Gerente
- El **Superusuario** es SOLO para el administrador del sistema
- El **Gerente** es para usuarios de confianza con acceso completo a la web pero NO al Django Admin
- Solo crea superusuarios cuando realmente lo necesites

### Seguridad
- Nunca compartas las credenciales del superusuario
- Para acceso administrativo general, usa el rol "Gerente"
- El Django Admin es solo para mantenimiento del sistema

### Rol Operador
- Los **Operadores** son usuarios especializados para el campo
- Tienen acceso limitado solo a Gastos y Maquinaria
- Pueden ser asignados como operadores en los registros de uso de maquinaria
- Ideal para personal que trabaja directamente con maquinaria y equipos

### Usos de Maquinaria Finalizados
- Los usos con `fecha_fin` y `horometro_final` están **finalizados**
- Solo los **Superusuarios** pueden editar/eliminar usos finalizados
- Esto previene modificaciones accidentales en registros históricos
