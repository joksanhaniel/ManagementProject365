from django.urls import path, include
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from . import views

# API REST Router
router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet, basename='cliente')
router.register(r'empleados', views.EmpleadoViewSet, basename='empleado')
router.register(r'proyectos', views.ProyectoViewSet, basename='proyecto')
router.register(r'asignaciones', views.AsignacionEmpleadoViewSet, basename='asignacion')
router.register(r'planillas', views.PlanillaViewSet, basename='planilla')
router.register(r'detalle-planillas', views.DetallePlanillaViewSet, basename='detalle-planilla')
router.register(r'gastos', views.GastoViewSet, basename='gasto')
router.register(r'pagos', views.PagoViewSet, basename='pago')

urlpatterns = [
    # Vistas HTML - Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_alt'),

    # Clientes - CRUD
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.cliente_delete, name='cliente_delete'),

    # Proveedores - CRUD
    path('proveedores/', views.proveedores_list, name='proveedores_list'),
    path('proveedores/nuevo/', views.proveedor_create, name='proveedor_create'),
    path('proveedores/<int:pk>/editar/', views.proveedor_update, name='proveedor_update'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_delete, name='proveedor_delete'),

    # Proyectos - CRUD
    path('proyectos/', views.proyectos_list, name='proyectos_list'),
    path('proyectos/nuevo/', views.proyecto_create, name='proyecto_create'),
    path('proyectos/<int:pk>/', views.proyecto_detail, name='proyecto_detail'),
    path('proyectos/<int:pk>/editar/', views.proyecto_update, name='proyecto_update'),
    path('proyectos/<int:pk>/eliminar/', views.proyecto_delete, name='proyecto_delete'),

    # Empleados - CRUD
    path('empleados/', views.empleados_list, name='empleados_list'),
    path('empleados/nuevo/', views.empleado_create, name='empleado_create'),
    path('empleados/<int:pk>/editar/', views.empleado_update, name='empleado_update'),
    path('empleados/<int:pk>/eliminar/', views.empleado_delete, name='empleado_delete'),

    # Asignaciones de Empleados - CRUD
    path('asignaciones/', views.asignaciones_list, name='asignaciones_list'),
    path('asignaciones/nueva/', views.asignacion_create, name='asignacion_create'),
    path('asignaciones/<int:pk>/editar/', views.asignacion_update, name='asignacion_update'),
    path('asignaciones/<int:pk>/eliminar/', views.asignacion_delete, name='asignacion_delete'),

    # Planillas - CRUD
    path('planillas/', views.planillas_list, name='planillas_list'),
    path('planillas/nueva/', views.planilla_create, name='planilla_create'),
    path('planillas/<int:pk>/editar/', views.planilla_update, name='planilla_update'),
    path('planillas/<int:pk>/eliminar/', views.planilla_delete, name='planilla_delete'),

    # AJAX - Obtener empleados de un proyecto
    path('proyectos/<int:proyecto_id>/empleados/', views.get_empleados_proyecto, name='get_empleados_proyecto'),

    # AJAX - Guardar secciones de planilla independientemente
    path('planillas/<int:pk>/save-empleados/', views.planilla_save_empleados, name='planilla_save_empleados'),
    path('planillas/<int:pk>/save-bonificaciones/', views.planilla_save_bonificaciones, name='planilla_save_bonificaciones'),
    path('planillas/<int:pk>/save-deducciones/', views.planilla_save_deducciones, name='planilla_save_deducciones'),
    path('planillas/<int:pk>/save-horas-extra/', views.planilla_save_horas_extra, name='planilla_save_horas_extra'),

    # Gastos - CRUD
    path('gastos/', views.gastos_list, name='gastos_list'),
    path('gastos/nuevo/', views.gasto_create, name='gasto_create'),
    path('gastos/<int:pk>/editar/', views.gasto_update, name='gasto_update'),
    path('gastos/<int:pk>/eliminar/', views.gasto_delete, name='gasto_delete'),

    # Usuarios - CRUD (Solo Administradores)
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/nuevo/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_update, name='usuario_update'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_delete, name='usuario_delete'),

    # Suscripciones SaaS
    path('renovar-licencia/', views.renovar_licencia, name='renovar_licencia'),
    path('reportar-pago/', views.reportar_pago, name='reportar_pago'),
    path('admin/confirmar-pagos/', views.confirmar_pagos, name='confirmar_pagos'),

    # Empresas - CRUD (Solo Superusuarios)
    path('empresas/', views.empresas_list, name='empresas_list'),
    path('empresas/nueva/', views.empresa_create, name='empresa_create'),
    path('empresas/<int:pk>/editar/', views.empresa_update, name='empresa_update'),
    path('empresas/<int:pk>/eliminar/', views.empresa_delete, name='empresa_delete'),

    # Órdenes de Cambio - CRUD
    path('ordenes-cambio/nueva/', views.orden_cambio_create, name='orden_cambio_create'),
    path('ordenes-cambio/<int:pk>/editar/', views.orden_cambio_update, name='orden_cambio_update'),
    path('ordenes-cambio/<int:pk>/eliminar/', views.orden_cambio_delete, name='orden_cambio_delete'),

    # Pagos (Desembolsos) - CRUD
    path('pagos/nuevo/', views.pago_create, name='pago_create'),
    path('pagos/<int:pk>/editar/', views.pago_update, name='pago_update'),
    path('pagos/<int:pk>/eliminar/', views.pago_delete, name='pago_delete'),

    # Maquinarias - CRUD
    path('maquinarias/', views.maquinarias_list, name='maquinarias_list'),
    path('maquinarias/nueva/', views.maquinaria_create, name='maquinaria_create'),
    path('maquinarias/<int:pk>/editar/', views.maquinaria_update, name='maquinaria_update'),
    path('maquinarias/<int:pk>/eliminar/', views.maquinaria_delete, name='maquinaria_delete'),
    path('maquinarias/<int:pk>/historial-tarifas/', views.maquinaria_historial_tarifas, name='maquinaria_historial_tarifas'),

    # AJAX endpoints
    path('api/maquinaria/<int:pk>/datos/', views.get_maquinaria_datos, name='get_maquinaria_datos'),

    # Uso de Maquinaria - CRUD
    path('usos-maquinaria/', views.usos_maquinaria_list, name='usos_maquinaria_list'),
    path('usos-maquinaria/nuevo/', views.uso_maquinaria_create, name='uso_maquinaria_create'),
    path('usos-maquinaria/<int:pk>/editar/', views.uso_maquinaria_update, name='uso_maquinaria_update'),
    path('usos-maquinaria/<int:pk>/eliminar/', views.uso_maquinaria_delete, name='uso_maquinaria_delete'),

    # API REST
    path('api/', include(router.urls)),
]
