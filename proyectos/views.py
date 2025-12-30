from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Count
from django.http import JsonResponse
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Cliente, Proveedor, Empleado, Proyecto, AsignacionEmpleado, Planilla,
    DetallePlanilla, Gasto, Pago, Usuario, OrdenCambio, Deduccion, Empresa
)
from .serializers import (
    ClienteSerializer, EmpleadoSerializer, ProyectoSerializer, ProyectoListSerializer,
    AsignacionEmpleadoSerializer, PlanillaSerializer, DetallePlanillaSerializer,
    GastoSerializer, PagoSerializer
)
from .forms import (
    ClienteForm, ProveedorForm, EmpleadoForm, ProyectoForm, GastoForm, PlanillaForm,
    DetallePlanillaFormSet, DeduccionFormSet, BonificacionFormSet, HoraExtraFormSet,
    UsuarioCreationForm, UsuarioUpdateForm
)
from .decorators import rol_requerido, permiso_escritura_requerido, permiso_financiero_requerido
from django.contrib import messages


# ====== HELPER FUNCTIONS ======

def get_empresa_from_request(request):
    """
    Obtiene la empresa del request (agregada por el middleware).
    Si el usuario es superusuario y no hay empresa en la URL, retorna None.
    Si el usuario normal no tiene empresa, retorna None.
    """
    return getattr(request, 'empresa', None)


# ====== VISTAS HTML (Templates) ======

class CustomLoginView(LoginView):
    template_name = 'proyectos/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Si es superusuario, redirigir a selección de empresa
        if self.request.user.is_superuser:
            return '/seleccionar-empresa/'
        # Si tiene empresa asignada, redirigir al dashboard de su empresa
        elif self.request.user.empresa:
            return f'/{self.request.user.empresa.get_url_prefix()}/dashboard/'
        else:
            # Usuario sin empresa asignada (no debería pasar)
            return '/dashboard/'


@login_required
def seleccionar_empresa(request):
    """
    Vista para que los superusuarios seleccionen con qué empresa trabajar.
    Los usuarios normales son redirigidos automáticamente a su empresa.
    """
    if not request.user.is_superuser:
        # Los usuarios normales van directo a su empresa
        if request.user.empresa:
            return redirect(f'/{request.user.empresa.get_url_prefix()}/dashboard/')
        else:
            messages.error(request, 'Usuario sin empresa asignada. Contacte al administrador.')
            return redirect('login')

    empresas = Empresa.objects.filter(activa=True).order_by('nombre')

    return render(request, 'proyectos/seleccionar_empresa.html', {
        'empresas': empresas,
    })

@login_required
def dashboard(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    # Filtrar proyectos por empresa
    if empresa:
        proyectos = Proyecto.objects.filter(empresa=empresa).select_related('cliente')
    else:
        proyectos = Proyecto.objects.select_related('cliente').all()

    proyectos_data = []

    utilidad_total = 0
    for proyecto in proyectos:
        costos = proyecto.calcular_costos_totales()
        utilidad = proyecto.calcular_utilidad_bruta()
        margen = proyecto.calcular_margen_utilidad()

        proyectos_data.append({
            'id': proyecto.id,
            'codigo': proyecto.codigo,
            'nombre': proyecto.nombre,
            'cliente': proyecto.cliente.nombre if proyecto.cliente else 'Sin Cliente',
            'estado': proyecto.estado,
            'monto_contrato': proyecto.monto_contrato,
            'costos_totales': costos,
            'utilidad_bruta': utilidad,
            'margen_utilidad': margen,
            'get_estado_display': proyecto.get_estado_display(),
        })
        utilidad_total += utilidad

    # Calcular estadísticas filtradas por empresa
    if empresa:
        stats = {
            'proyectos_activos': Proyecto.objects.filter(empresa=empresa, estado__in=['planificacion', 'en_progreso']).count(),
            'empleados_activos': Empleado.objects.filter(empresa=empresa, activo=True).count(),
            'gastos_pendientes': Gasto.objects.filter(proyecto__empresa=empresa, pagado=False).aggregate(total=Sum('monto'))['total'] or 0,
            'utilidad_total': utilidad_total,
        }
    else:
        stats = {
            'proyectos_activos': Proyecto.objects.filter(estado__in=['planificacion', 'en_progreso']).count(),
            'empleados_activos': Empleado.objects.filter(activo=True).count(),
            'gastos_pendientes': Gasto.objects.filter(pagado=False).aggregate(total=Sum('monto'))['total'] or 0,
            'utilidad_total': utilidad_total,
        }

    return render(request, 'proyectos/dashboard.html', {
        'stats': stats,
        'proyectos': proyectos_data,
    })


@login_required
def proyectos_list(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    # Filtrar proyectos por empresa
    if empresa:
        proyectos = Proyecto.objects.filter(empresa=empresa).select_related('cliente')
    else:
        proyectos = Proyecto.objects.select_related('cliente').all()

    # Filtros
    proyecto_id = request.GET.get('proyecto')
    estado = request.GET.get('estado')
    cliente_id = request.GET.get('cliente')

    if proyecto_id:
        proyectos = proyectos.filter(id=proyecto_id)
    if estado:
        proyectos = proyectos.filter(estado=estado)
    if cliente_id:
        proyectos = proyectos.filter(cliente_id=cliente_id)

    proyectos_data = []
    for proyecto in proyectos:
        proyectos_data.append({
            'id': proyecto.id,
            'codigo': proyecto.codigo,
            'nombre': proyecto.nombre,
            'cliente': proyecto.cliente,
            'estado': proyecto.estado,
            'monto_contrato': proyecto.monto_contrato,
            'costos_totales': proyecto.calcular_costos_totales(),
            'utilidad_bruta': proyecto.calcular_utilidad_bruta(),
            'margen_utilidad': proyecto.calcular_margen_utilidad(),
            'get_estado_display': proyecto.get_estado_display(),
        })

    # Datos para los filtros (filtrados por empresa)
    if empresa:
        clientes = Cliente.objects.filter(empresa=empresa, activo=True).order_by('nombre')
        todos_proyectos = Proyecto.objects.filter(empresa=empresa).order_by('codigo')
    else:
        clientes = Cliente.objects.filter(activo=True).order_by('nombre')
        todos_proyectos = Proyecto.objects.all().order_by('codigo')

    estados = Proyecto.ESTADO_CHOICES

    return render(request, 'proyectos/proyectos_list.html', {
        'proyectos': proyectos_data,
        'clientes': clientes,
        'estados': estados,
        'todos_proyectos': todos_proyectos,
        'filtro_proyecto': proyecto_id,
        'filtro_estado': estado,
        'filtro_cliente': cliente_id,
    })


@login_required
def proyecto_detail(request, pk, empresa_codigo=None):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    # Cálculos de costos
    costos_totales = proyecto.calcular_costos_totales()
    total_planillas = sum(p.monto_total for p in proyecto.planillas.all())
    total_gastos = sum(g.monto for g in proyecto.gastos.all())

    # Cálculos de ingresos
    monto_contrato_original = proyecto.monto_contrato
    total_ordenes_cambio = proyecto.calcular_total_ordenes_cambio()
    monto_total_proyecto = proyecto.calcular_monto_total_proyecto()

    # Cálculos de pagos del cliente
    total_pagado = proyecto.calcular_total_pagado()
    saldo_pendiente = proyecto.calcular_saldo_pendiente()
    porcentaje_pagado = proyecto.calcular_porcentaje_pagado()

    # Utilidad
    utilidad_bruta = proyecto.calcular_utilidad_bruta()
    margen_utilidad = proyecto.calcular_margen_utilidad()

    # Obtener desembolsos y órdenes de cambio
    desembolsos = proyecto.pagos.all().order_by('-fecha_pago')
    ordenes_cambio = proyecto.ordenes_cambio.all().order_by('-fecha_solicitud')

    return render(request, 'proyectos/proyecto_detail.html', {
        'proyecto': proyecto,
        'costos_totales': costos_totales,
        'total_planillas': total_planillas,
        'total_gastos': total_gastos,
        'monto_contrato_original': monto_contrato_original,
        'total_ordenes_cambio': total_ordenes_cambio,
        'monto_total_proyecto': monto_total_proyecto,
        'total_pagado': total_pagado,
        'saldo_pendiente': saldo_pendiente,
        'porcentaje_pagado': porcentaje_pagado,
        'utilidad_bruta': utilidad_bruta,
        'margen_utilidad': margen_utilidad,
        'desembolsos': desembolsos,
        'ordenes_cambio': ordenes_cambio,
    })


@login_required
def empleados_list(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    # Filtrar empleados por empresa
    if empresa:
        empleados = Empleado.objects.filter(empresa=empresa)
    else:
        empleados = Empleado.objects.all()

    # Filtros
    empleado_id = request.GET.get('empleado')
    activo = request.GET.get('activo')
    cargo = request.GET.get('cargo')
    tipo_contrato = request.GET.get('tipo_contrato')

    if empleado_id:
        empleados = empleados.filter(id=empleado_id)

    if activo:
        empleados = empleados.filter(activo=activo == '1')
    if cargo:
        empleados = empleados.filter(cargo__icontains=cargo)
    if tipo_contrato:
        empleados = empleados.filter(tipo_contrato=tipo_contrato)

    # Datos para filtros (filtrados por empresa)
    tipos_contrato = Empleado.TIPO_CONTRATO_CHOICES
    if empresa:
        cargos_unicos = Empleado.objects.filter(empresa=empresa).values_list('cargo', flat=True).distinct().order_by('cargo')
        todos_empleados = Empleado.objects.filter(empresa=empresa).order_by('apellidos', 'nombres')
    else:
        cargos_unicos = Empleado.objects.values_list('cargo', flat=True).distinct().order_by('cargo')
        todos_empleados = Empleado.objects.all().order_by('apellidos', 'nombres')

    return render(request, 'proyectos/empleados_list.html', {
        'empleados': empleados,
        'tipos_contrato': tipos_contrato,
        'cargos_unicos': cargos_unicos,
        'todos_empleados': todos_empleados,
        'filtro_empleado': empleado_id,
        'filtro_activo': activo,
        'filtro_cargo': cargo,
        'filtro_tipo_contrato': tipo_contrato,
    })


@login_required
def planillas_list(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    # Filtrar planillas por empresa (a través de proyecto)
    if empresa:
        planillas = Planilla.objects.filter(proyecto__empresa=empresa).select_related('proyecto')
    else:
        planillas = Planilla.objects.select_related('proyecto').all()

    # Filtros
    proyecto_id = request.GET.get('proyecto')
    tipo_planilla = request.GET.get('tipo_planilla')
    pagada = request.GET.get('pagada')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if proyecto_id:
        planillas = planillas.filter(proyecto_id=proyecto_id)
    if tipo_planilla:
        planillas = planillas.filter(tipo_planilla=tipo_planilla)
    if pagada:
        planillas = planillas.filter(pagada=pagada == '1')
    if fecha_desde:
        planillas = planillas.filter(fecha_pago__gte=fecha_desde)
    if fecha_hasta:
        planillas = planillas.filter(fecha_pago__lte=fecha_hasta)

    # Datos para filtros (filtrados por empresa)
    if empresa:
        proyectos = Proyecto.objects.filter(empresa=empresa, estado__in=['planificacion', 'en_progreso']).order_by('nombre')
    else:
        proyectos = Proyecto.objects.filter(estado__in=['planificacion', 'en_progreso']).order_by('nombre')

    tipos_planilla = Planilla.TIPO_PLANILLA_CHOICES

    return render(request, 'proyectos/planillas_list.html', {
        'planillas': planillas,
        'proyectos': proyectos,
        'tipos_planilla': tipos_planilla,
        'filtro_proyecto': proyecto_id,
        'filtro_tipo_planilla': tipo_planilla,
        'filtro_pagada': pagada,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
    })


@login_required
def gastos_list(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    # Filtrar gastos por empresa (a través de proyecto)
    if empresa:
        gastos = Gasto.objects.filter(proyecto__empresa=empresa).select_related('proyecto', 'proveedor')
    else:
        gastos = Gasto.objects.select_related('proyecto', 'proveedor').all()

    # Filtros
    proyecto_id = request.GET.get('proyecto')
    tipo_gasto = request.GET.get('tipo_gasto')
    proveedor_id = request.GET.get('proveedor')
    pagado = request.GET.get('pagado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if proyecto_id:
        gastos = gastos.filter(proyecto_id=proyecto_id)
    if tipo_gasto:
        gastos = gastos.filter(tipo_gasto=tipo_gasto)
    if proveedor_id:
        gastos = gastos.filter(proveedor_id=proveedor_id)
    if pagado:
        gastos = gastos.filter(pagado=pagado == '1')
    if fecha_desde:
        gastos = gastos.filter(fecha_gasto__gte=fecha_desde)
    if fecha_hasta:
        gastos = gastos.filter(fecha_gasto__lte=fecha_hasta)

    # Datos para filtros (filtrados por empresa)
    if empresa:
        proyectos = Proyecto.objects.filter(empresa=empresa).order_by('nombre')
        proveedores = Proveedor.objects.filter(empresa=empresa, activo=True).order_by('nombre')
    else:
        proyectos = Proyecto.objects.all().order_by('nombre')
        proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')

    tipos_gasto = Gasto.TIPO_GASTO_CHOICES

    return render(request, 'proyectos/gastos_list.html', {
        'gastos': gastos,
        'proyectos': proyectos,
        'tipos_gasto': tipos_gasto,
        'proveedores': proveedores,
        'filtro_proyecto': proyecto_id,
        'filtro_tipo_gasto': tipo_gasto,
        'filtro_proveedor': proveedor_id,
        'filtro_pagado': pagado,
        'filtro_fecha_desde': fecha_desde,
        'filtro_fecha_hasta': fecha_hasta,
    })


@login_required
def clientes_list(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    # Filtrar clientes por empresa
    if empresa:
        clientes = Cliente.objects.filter(empresa=empresa)
    else:
        clientes = Cliente.objects.all()

    # Filtros
    cliente_id = request.GET.get('cliente')
    estado = request.GET.get('estado')

    if cliente_id:
        clientes = clientes.filter(id=cliente_id)

    if estado == '1':
        clientes = clientes.filter(activo=True)
    elif estado == '0':
        clientes = clientes.filter(activo=False)

    # Datos para filtros (filtrados por empresa)
    if empresa:
        todos_clientes = Cliente.objects.filter(empresa=empresa).order_by('nombre')
    else:
        todos_clientes = Cliente.objects.all().order_by('nombre')

    return render(request, 'proyectos/clientes_list.html', {
        'clientes': clientes,
        'todos_clientes': todos_clientes,
        'filtro_cliente': cliente_id,
        'filtro_estado': estado,
    })


# ====== VISTAS CRUD (Create, Read, Update, Delete) ======

@login_required
def cliente_create(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.empresa = empresa  # Asignar empresa automáticamente
            cliente.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('clientes_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = ClienteForm()
    return render(request, 'proyectos/cliente_form.html', {'form': form})


@login_required
def cliente_update(request, pk, empresa_codigo=None):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('clientes_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'proyectos/cliente_form.html', {'form': form, 'object': cliente})


@login_required
def cliente_delete(request, pk, empresa_codigo=None):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente.')
        return redirect('clientes_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    return render(request, 'proyectos/confirm_delete.html', {'object': cliente, 'tipo': 'cliente'})


@login_required
def proveedores_list(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    # Filtrar proveedores por empresa
    if empresa:
        proveedores = Proveedor.objects.filter(empresa=empresa)
    else:
        proveedores = Proveedor.objects.all()

    # Filtros
    proveedor_id = request.GET.get('proveedor')
    activo = request.GET.get('activo')
    tipo_proveedor = request.GET.get('tipo_proveedor')

    if proveedor_id:
        proveedores = proveedores.filter(id=proveedor_id)

    if activo:
        proveedores = proveedores.filter(activo=activo == '1')
    if tipo_proveedor:
        proveedores = proveedores.filter(tipo_proveedor__icontains=tipo_proveedor)

    proveedores = proveedores.order_by('nombre')

    # Datos para filtros (filtrados por empresa)
    if empresa:
        tipos_proveedor_unicos = Proveedor.objects.filter(empresa=empresa).exclude(tipo_proveedor__isnull=True).exclude(tipo_proveedor='').values_list('tipo_proveedor', flat=True).distinct().order_by('tipo_proveedor')
        todos_proveedores = Proveedor.objects.filter(empresa=empresa).order_by('nombre')
    else:
        tipos_proveedor_unicos = Proveedor.objects.exclude(tipo_proveedor__isnull=True).exclude(tipo_proveedor='').values_list('tipo_proveedor', flat=True).distinct().order_by('tipo_proveedor')
        todos_proveedores = Proveedor.objects.all().order_by('nombre')

    return render(request, 'proyectos/proveedores_list.html', {
        'proveedores': proveedores,
        'tipos_proveedor_unicos': tipos_proveedor_unicos,
        'todos_proveedores': todos_proveedores,
        'filtro_proveedor': proveedor_id,
        'filtro_activo': activo,
        'filtro_tipo_proveedor': tipo_proveedor,
    })


@login_required
def proveedor_create(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            proveedor.empresa = empresa  # Asignar empresa automáticamente
            proveedor.save()
            messages.success(request, 'Proveedor creado exitosamente.')
            return redirect('proveedores_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = ProveedorForm()
    return render(request, 'proyectos/proveedor_form.html', {'form': form})


@login_required
def proveedor_update(request, pk, empresa_codigo=None):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente.')
            return redirect('proveedores_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'proyectos/proveedor_form.html', {'form': form, 'object': proveedor})


@login_required
def proveedor_delete(request, pk, empresa_codigo=None):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado exitosamente.')
        return redirect('proveedores_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    return render(request, 'proyectos/confirm_delete.html', {'object': proveedor, 'tipo': 'proveedor'})


@login_required
def proyecto_create(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    if request.method == 'POST':
        form = ProyectoForm(request.POST, empresa=empresa)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.empresa = empresa  # Asignar empresa automáticamente
            proyecto.save()
            messages.success(request, 'Proyecto creado exitosamente.')
            return redirect('proyectos_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = ProyectoForm(empresa=empresa)
    return render(request, 'proyectos/proyecto_form.html', {'form': form})


@login_required
def proyecto_update(request, pk, empresa_codigo=None):
    empresa = get_empresa_from_request(request)
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto, empresa=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proyecto actualizado exitosamente.')
            return redirect('proyecto_detail', empresa_codigo=request.empresa.codigo if request.empresa else 'default', pk=pk)
    else:
        form = ProyectoForm(instance=proyecto, empresa=empresa)
    return render(request, 'proyectos/proyecto_form.html', {'form': form, 'object': proyecto})


@login_required
def proyecto_delete(request, pk, empresa_codigo=None):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        proyecto.delete()
        messages.success(request, 'Proyecto eliminado exitosamente.')
        return redirect('proyectos_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    return render(request, 'proyectos/confirm_delete.html', {'object': proyecto, 'tipo': 'proyecto'})


@login_required
def empleado_create(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            empleado = form.save(commit=False)
            empleado.empresa = empresa  # Asignar empresa automáticamente
            empleado.save()
            messages.success(request, 'Empleado creado exitosamente.')
            return redirect('empleados_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = EmpleadoForm()
    return render(request, 'proyectos/empleado_form.html', {'form': form})


@login_required
def empleado_update(request, pk, empresa_codigo=None):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado exitosamente.')
            return redirect('empleados_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'proyectos/empleado_form.html', {'form': form, 'object': empleado})


@login_required
def empleado_delete(request, pk, empresa_codigo=None):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado exitosamente.')
        return redirect('empleados_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    return render(request, 'proyectos/confirm_delete.html', {'object': empleado, 'tipo': 'empleado'})


# ====== ASIGNACIONES DE EMPLEADOS ======

@login_required
def asignaciones_list(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    # Filtrar asignaciones por empresa (a través de proyecto)
    if empresa:
        asignaciones = AsignacionEmpleado.objects.filter(proyecto__empresa=empresa).select_related('proyecto', 'empleado')
    else:
        asignaciones = AsignacionEmpleado.objects.select_related('proyecto', 'empleado').all()

    return render(request, 'proyectos/asignaciones_list.html', {
        'asignaciones': asignaciones,
    })


@login_required
def asignacion_create(request, empresa_codigo=None):
    from .forms import AsignacionEmpleadoForm
    empresa = get_empresa_from_request(request)
    proyecto_id = request.GET.get('proyecto')

    if request.method == 'POST':
        form = AsignacionEmpleadoForm(request.POST, empresa=empresa)
        if form.is_valid():
            asignacion = form.save()
            messages.success(request, 'Empleado asignado exitosamente.')
            # Siempre redirigir al detalle del proyecto
            return redirect('proyecto_detail', pk=asignacion.proyecto.id)
    else:
        # Pre-seleccionar el proyecto si viene en la URL
        initial = {}
        if proyecto_id:
            initial['proyecto'] = proyecto_id
        form = AsignacionEmpleadoForm(initial=initial, empresa=empresa)

    return render(request, 'proyectos/asignacion_form.html', {'form': form})


@login_required
def asignacion_update(request, pk, empresa_codigo=None):
    from .forms import AsignacionEmpleadoForm
    empresa = get_empresa_from_request(request)
    asignacion = get_object_or_404(AsignacionEmpleado, pk=pk)
    proyecto_id = asignacion.proyecto.id

    if request.method == 'POST':
        form = AsignacionEmpleadoForm(request.POST, instance=asignacion, empresa=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignación actualizada exitosamente.')
            # Siempre redirigir al detalle del proyecto
            return redirect('proyecto_detail', empresa_codigo=request.empresa.codigo if request.empresa else 'default', pk=proyecto_id)
    else:
        form = AsignacionEmpleadoForm(instance=asignacion, empresa=empresa)
    return render(request, 'proyectos/asignacion_form.html', {'form': form, 'object': asignacion})


@login_required
def asignacion_delete(request, pk, empresa_codigo=None):
    asignacion = get_object_or_404(AsignacionEmpleado, pk=pk)
    proyecto_id = asignacion.proyecto.id  # Guardar antes de eliminar

    if request.method == 'POST':
        asignacion.delete()
        messages.success(request, 'Empleado desasignado exitosamente.')
        # Siempre redirigir al detalle del proyecto
        return redirect('proyecto_detail', empresa_codigo=request.empresa.codigo if request.empresa else 'default', pk=proyecto_id)
    return render(request, 'proyectos/confirm_delete.html', {'object': asignacion, 'tipo': 'asignación'})


@login_required
def gasto_create(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    if request.method == 'POST':
        form = GastoForm(request.POST, request.FILES, empresa=empresa)
        if form.is_valid():
            gasto = form.save()
            messages.success(request, 'Gasto registrado exitosamente.')
            return redirect('gastos_list', empresa_codigo=empresa.codigo if empresa else 'default')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = GastoForm(empresa=empresa)

    return render(request, 'proyectos/gasto_form.html', {
        'form': form,
        'empresa_codigo': empresa_codigo
    })


@login_required
def gasto_update(request, pk, empresa_codigo=None):
    empresa = get_empresa_from_request(request)
    gasto = get_object_or_404(Gasto, pk=pk)

    if request.method == 'POST':
        form = GastoForm(request.POST, request.FILES, instance=gasto, empresa=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gasto actualizado exitosamente.')
            return redirect('gastos_list', empresa_codigo=empresa.codigo if empresa else 'default')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = GastoForm(instance=gasto, empresa=empresa)

    return render(request, 'proyectos/gasto_form.html', {
        'form': form,
        'object': gasto,
        'empresa_codigo': empresa_codigo
    })


@login_required
def gasto_delete(request, pk, empresa_codigo=None):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        gasto.delete()
        messages.success(request, 'Gasto eliminado exitosamente.')
        return redirect('gastos_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    return render(request, 'proyectos/confirm_delete.html', {'object': gasto, 'tipo': 'gasto'})


@login_required
def planilla_create(request, empresa_codigo=None):
    empresa = get_empresa_from_request(request)

    if request.method == 'POST':
        form = PlanillaForm(request.POST, empresa=empresa)
        formset = DetallePlanillaFormSet(request.POST)
        bonificacion_formset = BonificacionFormSet(request.POST)
        horaextra_formset = HoraExtraFormSet(request.POST)
        deduccion_formset = DeduccionFormSet(request.POST)

        if form.is_valid() and formset.is_valid() and bonificacion_formset.is_valid() and horaextra_formset.is_valid() and deduccion_formset.is_valid():
            planilla = form.save()
            formset.instance = planilla
            bonificacion_formset.instance = planilla
            horaextra_formset.instance = planilla
            deduccion_formset.instance = planilla
            formset.save()
            bonificacion_formset.save()
            horaextra_formset.save()
            deduccion_formset.save()
            messages.success(request, 'Planilla creada exitosamente.')
            return redirect('planillas_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = PlanillaForm(empresa=empresa)
        formset = DetallePlanillaFormSet()
        bonificacion_formset = BonificacionFormSet()
        horaextra_formset = HoraExtraFormSet()
        deduccion_formset = DeduccionFormSet()

    # Obtener todos los empleados con su salario para JavaScript (filtrado por empresa)
    empleados = Empleado.objects.filter(empresa=empresa, activo=True).values('id', 'salario_base')
    empleados_salarios = {emp['id']: float(emp['salario_base']) for emp in empleados}

    # Obtener lista completa de empleados para los selects (filtrado por empresa)
    empleados_list = Empleado.objects.filter(empresa=empresa, activo=True).order_by('apellidos', 'nombres')

    return render(request, 'proyectos/planilla_form.html', {
        'form': form,
        'formset': formset,
        'bonificacion_formset': bonificacion_formset,
        'horaextra_formset': horaextra_formset,
        'deduccion_formset': deduccion_formset,
        'empleados_salarios': empleados_salarios,
        'empleados_list': empleados_list,
    })


@login_required
def planilla_update(request, pk, empresa_codigo=None):
    empresa = get_empresa_from_request(request)
    planilla = get_object_or_404(Planilla, pk=pk)

    if request.method == 'POST':
        form = PlanillaForm(request.POST, instance=planilla, empresa=empresa)
        formset = DetallePlanillaFormSet(request.POST, instance=planilla)
        bonificacion_formset = BonificacionFormSet(request.POST, instance=planilla)
        horaextra_formset = HoraExtraFormSet(request.POST, instance=planilla)
        deduccion_formset = DeduccionFormSet(request.POST, instance=planilla)

        if form.is_valid() and formset.is_valid() and bonificacion_formset.is_valid() and horaextra_formset.is_valid() and deduccion_formset.is_valid():
            form.save()
            formset.save()
            bonificacion_formset.save()
            horaextra_formset.save()
            deduccion_formset.save()
            messages.success(request, 'Planilla actualizada exitosamente.')
            return redirect('planillas_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = PlanillaForm(instance=planilla, empresa=empresa)
        formset = DetallePlanillaFormSet(instance=planilla)
        bonificacion_formset = BonificacionFormSet(instance=planilla)
        horaextra_formset = HoraExtraFormSet(instance=planilla)
        deduccion_formset = DeduccionFormSet(instance=planilla)

    # Obtener todos los empleados con su salario para JavaScript (filtrado por empresa)
    empleados = Empleado.objects.filter(empresa=empresa, activo=True).values('id', 'salario_base')
    empleados_salarios = {emp['id']: float(emp['salario_base']) for emp in empleados}

    # Obtener lista completa de empleados para los selects (filtrado por empresa)
    empleados_list = Empleado.objects.filter(empresa=empresa, activo=True).order_by('apellidos', 'nombres')

    return render(request, 'proyectos/planilla_form.html', {
        'form': form,
        'formset': formset,
        'bonificacion_formset': bonificacion_formset,
        'horaextra_formset': horaextra_formset,
        'deduccion_formset': deduccion_formset,
        'object': planilla,
        'empleados_salarios': empleados_salarios,
        'empleados_list': empleados_list,
    })


@login_required
def planilla_delete(request, pk, empresa_codigo=None):
    planilla = get_object_or_404(Planilla, pk=pk)
    if request.method == 'POST':
        planilla.delete()
        messages.success(request, 'Planilla eliminada exitosamente.')
        return redirect('planillas_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    return render(request, 'proyectos/confirm_delete.html', {'object': planilla, 'tipo': 'planilla'})


@login_required
def get_empleados_proyecto(request, proyecto_id):
    """Devuelve los empleados asignados activamente a un proyecto en formato JSON"""
    # Obtener las asignaciones activas del proyecto
    asignaciones = AsignacionEmpleado.objects.filter(
        proyecto_id=proyecto_id,
        activo=True,
        empleado__activo=True
    ).select_related('empleado')

    # Construir lista de empleados con su información
    empleados_data = []
    for asignacion in asignaciones:
        empleado = asignacion.empleado
        empleados_data.append({
            'id': empleado.id,
            'nombre_completo': empleado.nombre_completo,
            'salario_base': float(empleado.salario_base),
            'cargo': empleado.cargo,
        })

    return JsonResponse({'empleados': empleados_data})


@login_required
def planilla_save_empleados(request, pk, empresa_codigo=None):
    """Vista AJAX para guardar solo la sección de empleados de una planilla"""
    planilla = get_object_or_404(Planilla, pk=pk)

    if request.method == 'POST':
        formset = DetallePlanillaFormSet(request.POST, instance=planilla)

        if formset.is_valid():
            formset.save()

            # Recalcular el total de la planilla
            total_planilla = planilla.monto_total

            # Devolver los totales actualizados
            return JsonResponse({
                'success': True,
                'message': 'Empleados guardados exitosamente',
                'total_planilla': float(total_planilla),
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': formset.errors,
                'message': 'Error al guardar empleados'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
def planilla_save_bonificaciones(request, pk, empresa_codigo=None):
    """Vista AJAX para guardar solo la sección de bonificaciones de una planilla"""
    planilla = get_object_or_404(Planilla, pk=pk)

    if request.method == 'POST':
        formset = BonificacionFormSet(request.POST, instance=planilla)

        if formset.is_valid():
            formset.save()

            # Recalcular el total de la planilla
            total_planilla = planilla.monto_total

            return JsonResponse({
                'success': True,
                'message': 'Bonificaciones guardadas exitosamente',
                'total_planilla': float(total_planilla),
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': formset.errors,
                'message': 'Error al guardar bonificaciones'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
def planilla_save_deducciones(request, pk, empresa_codigo=None):
    """Vista AJAX para guardar solo la sección de deducciones de una planilla"""
    planilla = get_object_or_404(Planilla, pk=pk)

    if request.method == 'POST':
        formset = DeduccionFormSet(request.POST, instance=planilla)

        if formset.is_valid():
            formset.save()

            # Recalcular el total de la planilla
            total_planilla = planilla.monto_total

            return JsonResponse({
                'success': True,
                'message': 'Deducciones guardadas exitosamente',
                'total_planilla': float(total_planilla),
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': formset.errors,
                'message': 'Error al guardar deducciones'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
def planilla_save_horas_extra(request, pk, empresa_codigo=None):
    """Vista AJAX para guardar solo la sección de horas extra de una planilla"""
    planilla = get_object_or_404(Planilla, pk=pk)

    if request.method == 'POST':
        formset = HoraExtraFormSet(request.POST, instance=planilla)

        if formset.is_valid():
            formset.save()

            # Recalcular el total de la planilla
            total_planilla = planilla.monto_total

            return JsonResponse({
                'success': True,
                'message': 'Horas extra guardadas exitosamente',
                'total_planilla': float(total_planilla),
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': formset.errors,
                'message': 'Error al guardar horas extra'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


# ====== API REST (ViewSets) ======


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['codigo', 'nombre', 'rtn', 'email', 'contacto']
    filterset_fields = ['activo']
    ordering_fields = ['codigo', 'nombre']
    ordering = ['nombre']


class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['codigo', 'nombres', 'apellidos', 'dni', 'rtn']
    filterset_fields = ['activo', 'tipo_contrato', 'cargo']
    ordering_fields = ['codigo', 'apellidos', 'salario_base']
    ordering = ['apellidos']


class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.select_related('cliente').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['codigo', 'nombre', 'cliente__nombre']
    filterset_fields = ['estado']
    ordering_fields = ['codigo', 'fecha_inicio', 'monto_contrato']
    ordering = ['-fecha_inicio']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProyectoListSerializer
        return ProyectoSerializer

    @action(detail=True, methods=['get'])
    def utilidades(self, request, pk=None):
        """Endpoint para obtener el detalle de utilidades de un proyecto"""
        proyecto = self.get_object()
        return Response({
            'proyecto': {
                'codigo': proyecto.codigo,
                'nombre': proyecto.nombre,
                'cliente': proyecto.cliente,
            },
            'financiero': {
                'monto_contrato': float(proyecto.monto_contrato),
                'costos_totales': float(proyecto.calcular_costos_totales()),
                'utilidad_bruta': float(proyecto.calcular_utilidad_bruta()),
                'margen_utilidad': float(proyecto.calcular_margen_utilidad()),
            },
            'desglose_costos': {
                'total_planillas': float(sum(p.monto_total for p in proyecto.planillas.all())),
                'total_gastos': float(sum(g.monto for g in proyecto.gastos.all())),
            }
        })

    @action(detail=False, methods=['get'])
    def resumen_utilidades(self, request):
        """Endpoint para obtener resumen de utilidades de todos los proyectos"""
        proyectos = self.get_queryset()
        data = []

        for proyecto in proyectos:
            data.append({
                'id': proyecto.id,
                'codigo': proyecto.codigo,
                'nombre': proyecto.nombre,
                'cliente': proyecto.cliente,
                'estado': proyecto.estado,
                'monto_contrato': float(proyecto.monto_contrato),
                'costos_totales': float(proyecto.calcular_costos_totales()),
                'utilidad_bruta': float(proyecto.calcular_utilidad_bruta()),
                'margen_utilidad': float(proyecto.calcular_margen_utilidad()),
            })

        return Response(data)


class AsignacionEmpleadoViewSet(viewsets.ModelViewSet):
    queryset = AsignacionEmpleado.objects.all()
    serializer_class = AsignacionEmpleadoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['activo', 'proyecto', 'empleado']
    ordering = ['-fecha_asignacion']


class PlanillaViewSet(viewsets.ModelViewSet):
    queryset = Planilla.objects.all()
    serializer_class = PlanillaSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['pagada', 'tipo_planilla', 'proyecto']
    ordering = ['-fecha_pago']


class DetallePlanillaViewSet(viewsets.ModelViewSet):
    queryset = DetallePlanilla.objects.all()
    serializer_class = DetallePlanillaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['planilla', 'empleado']


class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.all()
    serializer_class = GastoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['descripcion', 'proveedor', 'numero_factura']
    filterset_fields = ['pagado', 'tipo_gasto', 'proyecto', 'categoria']
    ordering = ['-fecha_gasto']


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['forma_pago', 'proyecto']
    ordering = ['-fecha_pago']


# ========== GESTIÓN DE USUARIOS ==========

@login_required
def usuarios_list(request, empresa_codigo=None):
    """Vista para listar usuarios - Gerentes y Superusuarios"""
    # Validar permisos: Solo Gerentes y Superusuarios
    if not (request.user.is_superuser or request.user.rol == 'gerente'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    # Superusuarios ven todos los usuarios
    if request.user.is_superuser:
        usuarios = Usuario.objects.all()
    else:
        # Gerentes solo ven usuarios de SU empresa (excluyendo superusuarios)
        empresa = get_empresa_from_request(request)
        if empresa:
            usuarios = Usuario.objects.filter(empresa=empresa, is_superuser=False)
        else:
            usuarios = Usuario.objects.none()

    # Filtros
    rol = request.GET.get('rol')
    is_active = request.GET.get('is_active')

    if rol:
        usuarios = usuarios.filter(rol=rol)
    if is_active:
        usuarios = usuarios.filter(is_active=is_active == '1')

    usuarios = usuarios.order_by('username')

    # Datos para filtros
    roles = Usuario.ROL_CHOICES

    return render(request, 'proyectos/usuarios_list.html', {
        'usuarios': usuarios,
        'roles': roles,
        'filtro_rol': rol,
        'filtro_is_active': is_active,
    })


@login_required
def usuario_create(request, empresa_codigo=None):
    """Vista para crear usuario - Gerentes y Superusuarios"""
    # Validar permisos: Solo Gerentes y Superusuarios
    if not (request.user.is_superuser or request.user.rol == 'gerente'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    empresa = get_empresa_from_request(request)

    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            # Si es Gerente (NO superusuario), forzar la empresa a la suya
            if not request.user.is_superuser:
                if empresa:
                    usuario.empresa = empresa
                else:
                    messages.error(request, 'No se puede crear usuario: no tienes empresa asignada.')
                    return redirect('usuarios_list', empresa_codigo=empresa_codigo or 'default')

            # Validar que Gerente no pueda crear superusuarios
            if not request.user.is_superuser and usuario.is_superuser:
                messages.error(request, 'No tienes permisos para crear superusuarios.')
                return redirect('usuarios_list', empresa_codigo=empresa_codigo or 'default')

            usuario.save()
            form.save_m2m()  # Guardar relaciones many-to-many si existen
            messages.success(request, f'Usuario {usuario.username} creado exitosamente.')
            return redirect('usuarios_list', empresa_codigo=empresa.codigo if empresa else 'default')
    else:
        form = UsuarioCreationForm()

        # Si es Gerente, pre-seleccionar y bloquear su empresa
        if not request.user.is_superuser and empresa:
            form.initial['empresa'] = empresa

    return render(request, 'proyectos/usuario_form.html', {
        'form': form,
        'es_gerente': request.user.rol == 'gerente' and not request.user.is_superuser,
    })


@login_required
def usuario_update(request, pk, empresa_codigo=None):
    """Vista para editar usuario - Gerentes y Superusuarios"""
    # Validar permisos: Solo Gerentes y Superusuarios
    if not (request.user.is_superuser or request.user.rol == 'gerente'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    usuario = get_object_or_404(Usuario, pk=pk)
    empresa = get_empresa_from_request(request)

    # Validar que Gerente solo pueda editar usuarios de SU empresa
    if not request.user.is_superuser:
        if usuario.empresa != empresa:
            messages.error(request, 'No tienes permisos para editar usuarios de otra empresa.')
            return redirect('usuarios_list', empresa_codigo=empresa.codigo if empresa else 'default')

    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario_editado = form.save(commit=False)

            # Si es Gerente (NO superusuario), no puede cambiar la empresa
            if not request.user.is_superuser:
                usuario_editado.empresa = empresa

            # Validar que Gerente no pueda convertir a superusuario
            if not request.user.is_superuser and usuario_editado.is_superuser:
                messages.error(request, 'No tienes permisos para convertir usuarios en superusuarios.')
                return redirect('usuarios_list', empresa_codigo=empresa.codigo if empresa else 'default')

            usuario_editado.save()
            messages.success(request, f'Usuario {usuario_editado.username} actualizado exitosamente.')
            return redirect('usuarios_list', empresa_codigo=empresa.codigo if empresa else 'default')
    else:
        form = UsuarioUpdateForm(instance=usuario)

    return render(request, 'proyectos/usuario_form.html', {
        'form': form,
        'object': usuario,
        'es_gerente': request.user.rol == 'gerente' and not request.user.is_superuser,
    })


@login_required
def usuario_delete(request, pk, empresa_codigo=None):
    """Vista para eliminar usuario - Gerentes y Superusuarios"""
    # Validar permisos: Solo Gerentes y Superusuarios
    if not (request.user.is_superuser or request.user.rol == 'gerente'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    usuario = get_object_or_404(Usuario, pk=pk)
    empresa = get_empresa_from_request(request)

    # Validar que Gerente solo pueda eliminar usuarios de SU empresa
    if not request.user.is_superuser:
        if usuario.empresa != empresa:
            messages.error(request, 'No tienes permisos para eliminar usuarios de otra empresa.')
            return redirect('usuarios_list', empresa_codigo=empresa.codigo if empresa else 'default')

        # Gerente no puede eliminar superusuarios
        if usuario.is_superuser:
            messages.error(request, 'No tienes permisos para eliminar superusuarios.')
            return redirect('usuarios_list', empresa_codigo=empresa.codigo if empresa else 'default')

    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario {username} eliminado exitosamente.')
        return redirect('usuarios_list', empresa_codigo=empresa.codigo if empresa else 'default')
    return render(request, 'proyectos/confirm_delete.html', {'object': usuario, 'tipo': 'usuario'})


# ====== VISTAS DE ÓRDENES DE CAMBIO ======

@login_required
@permiso_escritura_requerido
def orden_cambio_create(request):
    """Vista para crear orden de cambio - Requiere permiso de escritura"""
    if request.method == 'POST':
        proyecto_id = request.POST.get('proyecto')
        codigo = request.POST.get('codigo')
        descripcion = request.POST.get('descripcion')
        monto_adicional = request.POST.get('monto_adicional')
        fecha_solicitud = request.POST.get('fecha_solicitud')
        estado = request.POST.get('estado', 'pendiente')
        fecha_aprobacion = request.POST.get('fecha_aprobacion') or None

        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)

        orden = OrdenCambio.objects.create(
            proyecto=proyecto,
            codigo=codigo,
            descripcion=descripcion,
            monto_adicional=monto_adicional,
            fecha_solicitud=fecha_solicitud,
            fecha_aprobacion=fecha_aprobacion,
            estado=estado
        )

        messages.success(request, f'Orden de cambio {orden.codigo} creada exitosamente.')
        return redirect('proyecto_detail', pk=proyecto.id)

    # GET request
    proyecto_id = request.GET.get('proyecto')
    proyectos = Proyecto.objects.all()
    proyecto_seleccionado = None
    if proyecto_id:
        proyecto_seleccionado = get_object_or_404(Proyecto, pk=proyecto_id)

    return render(request, 'proyectos/orden_cambio_form.html', {
        'proyectos': proyectos,
        'proyecto_seleccionado': proyecto_seleccionado,
    })


@login_required
@permiso_escritura_requerido
def orden_cambio_update(request, pk):
    """Vista para editar orden de cambio - Requiere permiso de escritura"""
    orden = get_object_or_404(OrdenCambio, pk=pk)

    if request.method == 'POST':
        orden.codigo = request.POST.get('codigo')
        orden.descripcion = request.POST.get('descripcion')
        orden.monto_adicional = request.POST.get('monto_adicional')
        orden.fecha_solicitud = request.POST.get('fecha_solicitud')
        orden.estado = request.POST.get('estado')
        fecha_aprobacion = request.POST.get('fecha_aprobacion')
        orden.fecha_aprobacion = fecha_aprobacion if fecha_aprobacion else None

        orden.save()

        messages.success(request, f'Orden de cambio {orden.codigo} actualizada exitosamente.')
        return redirect('proyecto_detail', pk=orden.proyecto.id)

    proyectos = Proyecto.objects.all()

    return render(request, 'proyectos/orden_cambio_form.html', {
        'orden': orden,
        'proyectos': proyectos,
        'proyecto_seleccionado': orden.proyecto,
    })


@login_required
@permiso_escritura_requerido
def orden_cambio_delete(request, pk):
    """Vista para eliminar orden de cambio - Requiere permiso de escritura"""
    orden = get_object_or_404(OrdenCambio, pk=pk)
    proyecto_id = orden.proyecto.id

    if request.method == 'POST':
        codigo = orden.codigo
        orden.delete()
        messages.success(request, f'Orden de cambio {codigo} eliminada exitosamente.')
        return redirect('proyecto_detail', empresa_codigo=request.empresa.codigo if request.empresa else 'default', pk=proyecto_id)

    return render(request, 'proyectos/confirm_delete.html', {
        'object': orden,
        'tipo': 'orden de cambio',
        'objeto_nombre': orden.codigo
    })


# ====== VISTAS DE PAGOS (DESEMBOLSOS) ======

@login_required
@permiso_financiero_requerido
def pago_create(request, empresa_codigo=None):
    """Vista para registrar pago/desembolso del cliente - Requiere permiso financiero"""
    if request.method == 'POST':
        proyecto_id = request.POST.get('proyecto')
        concepto = request.POST.get('concepto')
        monto = request.POST.get('monto')
        fecha_pago = request.POST.get('fecha_pago')
        forma_pago = request.POST.get('forma_pago')
        numero_referencia = request.POST.get('numero_referencia')

        proyecto = get_object_or_404(Proyecto, pk=proyecto_id)

        pago = Pago.objects.create(
            proyecto=proyecto,
            concepto=concepto,
            monto=monto,
            fecha_pago=fecha_pago,
            forma_pago=forma_pago,
            numero_referencia=numero_referencia
        )

        messages.success(request, f'Pago de ${monto} registrado exitosamente.')
        return redirect('proyecto_detail', pk=proyecto.id)

    # GET request
    proyecto_id = request.GET.get('proyecto')
    proyectos = Proyecto.objects.all()
    proyecto_seleccionado = None
    if proyecto_id:
        proyecto_seleccionado = get_object_or_404(Proyecto, pk=proyecto_id)

    return render(request, 'proyectos/pago_form.html', {
        'proyectos': proyectos,
        'proyecto_seleccionado': proyecto_seleccionado,
    })


@login_required
@permiso_financiero_requerido
def pago_update(request, pk, empresa_codigo=None):
    """Vista para editar pago/desembolso - Requiere permiso financiero"""
    pago = get_object_or_404(Pago, pk=pk)

    if request.method == 'POST':
        pago.concepto = request.POST.get('concepto')
        pago.monto = request.POST.get('monto')
        pago.fecha_pago = request.POST.get('fecha_pago')
        pago.forma_pago = request.POST.get('forma_pago')
        pago.numero_referencia = request.POST.get('numero_referencia')

        pago.save()

        messages.success(request, 'Pago actualizado exitosamente.')
        return redirect('proyecto_detail', pk=pago.proyecto.id)

    proyectos = Proyecto.objects.all()

    return render(request, 'proyectos/pago_form.html', {
        'pago': pago,
        'proyectos': proyectos,
        'proyecto_seleccionado': pago.proyecto,
    })


@login_required
@permiso_financiero_requerido
def pago_delete(request, pk, empresa_codigo=None):
    """Vista para eliminar pago/desembolso - Requiere permiso financiero"""
    pago = get_object_or_404(Pago, pk=pk)
    proyecto_id = pago.proyecto.id

    if request.method == 'POST':
        monto = pago.monto
        pago.delete()
        messages.success(request, f'Pago de ${monto} eliminado exitosamente.')
        return redirect('proyecto_detail', empresa_codigo=request.empresa.codigo if request.empresa else 'default', pk=proyecto_id)

    return render(request, 'proyectos/confirm_delete.html', {
        'object': pago,
        'tipo': 'pago',
        'objeto_nombre': f'${pago.monto} del {pago.fecha_pago}'
    })


# ====== VISTAS DE GESTIÓN DE EMPRESAS (SOLO SUPERUSUARIOS) ======

@login_required
def empresas_list(request, empresa_codigo=None):
    """Vista para listar todas las empresas - Solo para superusuarios"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    from .models import Empresa
    empresas = Empresa.objects.all().order_by('nombre')

    return render(request, 'proyectos/empresas_list.html', {
        'empresas': empresas,
    })


@login_required
def empresa_create(request, empresa_codigo=None):
    """Vista para crear nueva empresa - Solo para superusuarios"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    from .forms import EmpresaForm

    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa creada exitosamente.')
            return redirect('empresas_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = EmpresaForm()

    return render(request, 'proyectos/empresa_form.html', {'form': form})


@login_required
def empresa_update(request, pk, empresa_codigo=None):
    """Vista para editar empresa - Solo para superusuarios"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    from .models import Empresa
    from .forms import EmpresaForm

    empresa = get_object_or_404(Empresa, pk=pk)

    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa actualizada exitosamente.')
            return redirect('empresas_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')
    else:
        form = EmpresaForm(instance=empresa)

    return render(request, 'proyectos/empresa_form.html', {'form': form, 'object': empresa})


@login_required
def empresa_delete(request, pk, empresa_codigo=None):
    """Vista para eliminar empresa - Solo para superusuarios"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    from .models import Empresa

    empresa = get_object_or_404(Empresa, pk=pk)

    if request.method == 'POST':
        empresa.delete()
        messages.success(request, 'Empresa eliminada exitosamente.')
        return redirect('empresas_list', empresa_codigo=request.empresa.codigo if request.empresa else 'default')

    return render(request, 'proyectos/confirm_delete.html', {'object': empresa, 'tipo': 'empresa'})


