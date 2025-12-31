from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    Cliente, Proveedor, Empleado, Proyecto, AsignacionEmpleado, Planilla,
    DetallePlanilla, Gasto, Pago, Usuario, OrdenCambio, Deduccion,
    Bonificacion, HoraExtra, HistorialSalario, Empresa, RegistroTrial,
    PagoRecibido
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'rtn', 'telefono', 'contacto', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre', 'rtn', 'email', 'contacto')
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('codigo', 'nombre', 'rtn')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion', 'contacto')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'rtn', 'tipo_proveedor', 'telefono', 'contacto', 'activo')
    list_filter = ('activo', 'tipo_proveedor')
    search_fields = ('codigo', 'nombre', 'rtn', 'email', 'contacto')
    fieldsets = (
        ('Información del Proveedor', {
            'fields': ('codigo', 'nombre', 'rtn', 'tipo_proveedor')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion', 'contacto')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


class DetallePlanillaInline(admin.TabularInline):
    model = DetallePlanilla
    extra = 1
    autocomplete_fields = ['empleado']
    fields = ('empleado', 'salario_devengado')
    readonly_fields = ('salario_devengado',)

    def get_readonly_fields(self, request, obj=None):
        # Opcionalmente puedes hacer que salario_devengado sea readonly
        # si quieres que se calcule automáticamente
        return ()


class AsignacionEmpleadoInline(admin.TabularInline):
    model = AsignacionEmpleado
    extra = 1
    autocomplete_fields = ['empleado']
    fields = ('empleado', 'fecha_asignacion', 'fecha_finalizacion', 'activo')


class PlanillaInline(admin.TabularInline):
    model = Planilla
    extra = 0
    fields = ('periodo_inicio', 'periodo_fin', 'tipo_planilla', 'fecha_pago', 'pagada')
    readonly_fields = ('periodo_inicio', 'periodo_fin', 'tipo_planilla', 'fecha_pago')
    can_delete = False


class GastoInline(admin.TabularInline):
    model = Gasto
    extra = 1
    fields = ('tipo_gasto', 'descripcion', 'monto', 'fecha_gasto', 'pagado')


class DeduccionInline(admin.TabularInline):
    model = Deduccion
    extra = 1
    autocomplete_fields = ['empleado']
    fields = ('empleado', 'descripcion', 'monto', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)


class BonificacionInline(admin.TabularInline):
    model = Bonificacion
    extra = 1
    autocomplete_fields = ['empleado']
    fields = ('empleado', 'descripcion', 'monto', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)


class HoraExtraInline(admin.TabularInline):
    model = HoraExtra
    extra = 1
    autocomplete_fields = ['empleado']
    fields = ('empleado', 'descripcion', 'cantidad_horas', 'monto', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)


class HistorialSalarioInline(admin.TabularInline):
    model = HistorialSalario
    extra = 0
    can_delete = False
    fields = ('salario_anterior', 'salario_nuevo', 'fecha_cambio', 'usuario', 'motivo')
    readonly_fields = ('salario_anterior', 'salario_nuevo', 'fecha_cambio', 'usuario')

    def has_add_permission(self, request, obj=None):
        # No permitir agregar manualmente, solo se crea automáticamente
        return False


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre_completo', 'cargo', 'tipo_contrato', 'salario_base', 'activo')
    list_filter = ('activo', 'tipo_contrato', 'cargo')
    search_fields = ('codigo', 'nombres', 'apellidos', 'dni', 'rtn')
    readonly_fields = ('nombre_completo',)
    inlines = [HistorialSalarioInline]
    fieldsets = (
        ('Información Personal', {
            'fields': ('codigo', 'nombres', 'apellidos', 'dni', 'rtn', 'telefono', 'direccion')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'tipo_contrato', 'salario_base', 'fecha_ingreso', 'activo')
        }),
    )


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'cliente', 'monto_contrato', 'estado', 'porcentaje_avance', 'utilidad_display')
    list_filter = ('estado', 'fecha_inicio')
    search_fields = ('codigo', 'nombre', 'cliente')
    inlines = [AsignacionEmpleadoInline, PlanillaInline, GastoInline]
    readonly_fields = ('costos_totales_display', 'utilidad_bruta_display', 'margen_utilidad_display')

    fieldsets = (
        ('Información del Proyecto', {
            'fields': ('codigo', 'nombre', 'descripcion', 'cliente', 'direccion')
        }),
        ('Información Financiera', {
            'fields': ('monto_contrato', 'costos_totales_display', 'utilidad_bruta_display', 'margen_utilidad_display')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real', 'estado', 'porcentaje_avance')
        }),
    )

    def costos_totales_display(self, obj):
        if obj.pk:
            costos = obj.calcular_costos_totales()
            return format_html('<strong>${:,.2f}</strong>', costos)
        return '-'
    costos_totales_display.short_description = 'Costos Totales'

    def utilidad_bruta_display(self, obj):
        if obj.pk:
            utilidad = obj.calcular_utilidad_bruta()
            color = 'green' if utilidad > 0 else 'red'
            return format_html('<strong style="color: {};">${:,.2f}</strong>', color, utilidad)
        return '-'
    utilidad_bruta_display.short_description = 'Utilidad Bruta'

    def margen_utilidad_display(self, obj):
        if obj.pk:
            margen = obj.calcular_margen_utilidad()
            color = 'green' if margen > 0 else 'red'
            return format_html('<strong style="color: {};">{:.2f}%</strong>', color, margen)
        return '-'
    margen_utilidad_display.short_description = 'Margen de Utilidad'

    def utilidad_display(self, obj):
        utilidad = obj.calcular_utilidad_bruta()
        color = 'green' if utilidad > 0 else 'red'
        return format_html('<span style="color: {};">${:,.2f}</span>', color, utilidad)
    utilidad_display.short_description = 'Utilidad'


@admin.register(AsignacionEmpleado)
class AsignacionEmpleadoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'proyecto', 'fecha_asignacion', 'fecha_finalizacion', 'activo')
    list_filter = ('activo', 'fecha_asignacion', 'proyecto')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'proyecto__nombre', 'proyecto__codigo')
    autocomplete_fields = ['empleado', 'proyecto']


@admin.register(Planilla)
class PlanillaAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'periodo_inicio', 'periodo_fin', 'tipo_planilla', 'fecha_pago', 'monto_total_display', 'pagada')
    list_filter = ('pagada', 'tipo_planilla', 'fecha_pago')
    search_fields = ('proyecto__codigo', 'proyecto__nombre')
    autocomplete_fields = ['proyecto']
    inlines = [DetallePlanillaInline, BonificacionInline, HoraExtraInline, DeduccionInline]
    readonly_fields = ('monto_total_display',)

    fieldsets = (
        ('Información de Planilla', {
            'fields': ('proyecto', 'periodo_inicio', 'periodo_fin', 'tipo_planilla')
        }),
        ('Pago', {
            'fields': ('fecha_pago', 'monto_total_display', 'pagada', 'observaciones')
        }),
    )

    def monto_total_display(self, obj):
        if obj.pk:
            return format_html('<strong>${:,.2f}</strong>', obj.monto_total)
        return '-'
    monto_total_display.short_description = 'Monto Total'


@admin.register(DetallePlanilla)
class DetallePlanillaAdmin(admin.ModelAdmin):
    list_display = ('planilla', 'empleado', 'salario_devengado', 'bonificaciones_display', 'deducciones_display', 'horas_extra_display', 'total_display')
    list_filter = ('planilla__fecha_pago', 'empleado')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'planilla__proyecto__codigo')
    autocomplete_fields = ['planilla', 'empleado']
    readonly_fields = ('salario_devengado',)

    def bonificaciones_display(self, obj):
        total = obj.calcular_total_bonificaciones()
        return format_html('<span>${:,.2f}</span>', total)
    bonificaciones_display.short_description = 'Bonificaciones'

    def deducciones_display(self, obj):
        total = obj.calcular_total_deducciones()
        return format_html('<span>${:,.2f}</span>', total)
    deducciones_display.short_description = 'Deducciones'

    def horas_extra_display(self, obj):
        total = obj.calcular_monto_horas_extra()
        return format_html('<span>${:,.2f}</span>', total)
    horas_extra_display.short_description = 'Horas Extra'

    def total_display(self, obj):
        return format_html('<strong>${:,.2f}</strong>', obj.calcular_total())
    total_display.short_description = 'Total a Pagar'


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'tipo_gasto', 'descripcion_corta', 'proveedor', 'monto', 'fecha_gasto', 'pagado')
    list_filter = ('pagado', 'tipo_gasto', 'fecha_gasto')
    search_fields = ('proyecto__codigo', 'proyecto__nombre', 'descripcion', 'proveedor__nombre', 'numero_factura')
    autocomplete_fields = ['proyecto', 'proveedor']

    fieldsets = (
        ('Información del Gasto', {
            'fields': ('proyecto', 'tipo_gasto', 'descripcion')
        }),
        ('Detalles Financieros', {
            'fields': ('monto', 'proveedor', 'numero_factura', 'fecha_gasto')
        }),
        ('Estado de Pago', {
            'fields': ('pagado', 'fecha_pago')
        }),
    )

    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'concepto', 'monto', 'fecha_pago', 'forma_pago', 'numero_referencia')
    list_filter = ('forma_pago', 'fecha_pago')
    search_fields = ('proyecto__codigo', 'proyecto__nombre', 'concepto', 'numero_referencia')
    autocomplete_fields = ['proyecto']

    fieldsets = (
        ('Información del Pago', {
            'fields': ('proyecto', 'concepto', 'monto')
        }),
        ('Detalles de Pago', {
            'fields': ('fecha_pago', 'forma_pago', 'numero_referencia')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )


@admin.register(OrdenCambio)
class OrdenCambioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'proyecto', 'descripcion_corta', 'monto_adicional', 'estado', 'fecha_solicitud', 'fecha_aprobacion')
    list_filter = ('estado', 'fecha_solicitud')
    search_fields = ('codigo', 'proyecto__codigo', 'proyecto__nombre', 'descripcion')
    autocomplete_fields = ['proyecto']

    fieldsets = (
        ('Información de la Orden', {
            'fields': ('proyecto', 'codigo', 'descripcion')
        }),
        ('Datos Financieros', {
            'fields': ('monto_adicional',)
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_solicitud', 'fecha_aprobacion', 'estado')
        }),
        ('Responsable', {
            'fields': ('solicitado_por', 'justificacion')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )

    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'rol')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono')}),
        ('Permisos y Rol', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined', 'fecha_creacion', 'fecha_modificacion')}),
    )

    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'last_login', 'date_joined')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'rol', 'is_staff', 'is_active'),
        }),
    )


@admin.register(Deduccion)
class DeduccionAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'planilla', 'descripcion', 'monto', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'planilla__fecha_pago')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'descripcion', 'planilla__proyecto__nombre')
    autocomplete_fields = ['planilla', 'empleado']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)

    fieldsets = (
        ('Información de la Deducción', {
            'fields': ('planilla', 'empleado', 'descripcion', 'monto')
        }),
        ('Fecha', {
            'fields': ('fecha_creacion',)
        }),
    )


@admin.register(Bonificacion)
class BonificacionAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'planilla', 'descripcion', 'monto', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'planilla__fecha_pago')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'descripcion', 'planilla__proyecto__nombre')
    autocomplete_fields = ['planilla', 'empleado']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)

    fieldsets = (
        ('Información de la Bonificación', {
            'fields': ('planilla', 'empleado', 'descripcion', 'monto')
        }),
        ('Fecha', {
            'fields': ('fecha_creacion',)
        }),
    )


@admin.register(HoraExtra)
class HoraExtraAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'planilla', 'descripcion', 'cantidad_horas', 'monto', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'planilla__fecha_pago')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'descripcion', 'planilla__proyecto__nombre')
    autocomplete_fields = ['planilla', 'empleado']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)

    fieldsets = (
        ('Información de Horas Extra', {
            'fields': ('planilla', 'empleado', 'descripcion', 'cantidad_horas', 'monto')
        }),
        ('Fecha', {
            'fields': ('fecha_creacion',)
        }),
    )


@admin.register(HistorialSalario)
class HistorialSalarioAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'salario_anterior', 'salario_nuevo', 'fecha_cambio', 'usuario', 'motivo')
    list_filter = ('fecha_cambio', 'empleado')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'motivo')
    autocomplete_fields = ['empleado', 'usuario']
    date_hierarchy = 'fecha_cambio'
    readonly_fields = ('salario_anterior', 'salario_nuevo', 'fecha_cambio', 'usuario')

    fieldsets = (
        ('Información del Cambio', {
            'fields': ('empleado', 'salario_anterior', 'salario_nuevo', 'fecha_cambio')
        }),
        ('Responsable', {
            'fields': ('usuario', 'motivo')
        }),
    )

    def has_add_permission(self, request):
        # No permitir agregar manualmente desde el admin principal
        return False

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar historial
        return False


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'razon_social', 'rtn', 'email', 'tipo_suscripcion', 'fecha_expiracion_suscripcion', 'activa')
    list_filter = ('activa', 'tipo_suscripcion', 'estado_suscripcion', 'fecha_expiracion_suscripcion')
    search_fields = ('codigo', 'nombre', 'razon_social', 'rtn', 'email')
    readonly_fields = ('codigo', 'fecha_creacion', 'fecha_modificacion', 'ip_registro')

    fieldsets = (
        ('Información de la Empresa', {
            'fields': ('codigo', 'nombre', 'razon_social', 'rtn', 'telefono', 'email', 'direccion')
        }),
        ('Suscripción', {
            'fields': ('plan_elegido', 'tipo_suscripcion', 'estado_suscripcion', 'fecha_inicio_suscripcion', 'fecha_expiracion_suscripcion', 'cuota_instalacion_pagada', 'plan_incluye_maquinaria', 'activa')
        }),
        ('Seguridad y Registro', {
            'fields': ('ip_registro', 'fecha_creacion', 'fecha_modificacion')
        }),
    )


@admin.register(RegistroTrial)
class RegistroTrialAdmin(admin.ModelAdmin):
    list_display = ('email_empresa', 'email_usuario', 'ip_address', 'rtn', 'fecha_registro', 'bloqueado', 'empresa_creada')
    list_filter = ('bloqueado', 'fecha_registro')
    search_fields = ('email_empresa', 'email_usuario', 'ip_address', 'rtn')
    readonly_fields = ('fecha_registro',)
    date_hierarchy = 'fecha_registro'

    fieldsets = (
        ('Información de Registro', {
            'fields': ('ip_address', 'email_empresa', 'email_usuario', 'rtn', 'empresa_creada')
        }),
        ('Fecha', {
            'fields': ('fecha_registro',)
        }),
        ('Control de Abuso', {
            'fields': ('bloqueado', 'motivo_bloqueo')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # Hacer todos los campos readonly excepto bloqueado y motivo_bloqueo
        if obj:  # Editando un registro existente
            return self.readonly_fields + ('ip_address', 'email_empresa', 'email_usuario', 'rtn', 'empresa_creada')
        return self.readonly_fields


@admin.register(PagoRecibido)
class PagoRecibidoAdmin(admin.ModelAdmin):
    list_display = (
        'empresa',
        'monto_formateado',
        'plan_seleccionado_corto',
        'fecha_pago',
        'metodo_pago',
        'estado_badge',
        'fecha_registro'
    )
    list_filter = ('estado', 'metodo_pago', 'plan_seleccionado', 'fecha_pago', 'fecha_registro')
    search_fields = ('empresa__nombre', 'empresa__rtn', 'referencia', 'notas_cliente', 'notas_admin')
    readonly_fields = ('fecha_registro', 'fecha_confirmacion', 'confirmado_por', 'ver_comprobante')
    date_hierarchy = 'fecha_pago'
    actions = ['confirmar_pagos_seleccionados', 'rechazar_pagos_seleccionados']

    fieldsets = (
        ('Información del Pago', {
            'fields': ('empresa', 'monto', 'fecha_pago', 'metodo_pago', 'plan_seleccionado')
        }),
        ('Comprobante', {
            'fields': ('comprobante', 'ver_comprobante', 'referencia', 'notas_cliente')
        }),
        ('Estado y Gestión', {
            'fields': ('estado', 'notas_admin', 'fecha_registro', 'fecha_confirmacion', 'confirmado_por')
        }),
    )

    def monto_formateado(self, obj):
        return f"L. {obj.monto:,.2f}"
    monto_formateado.short_description = 'Monto'
    monto_formateado.admin_order_field = 'monto'

    def plan_seleccionado_corto(self, obj):
        # Mostrar versión corta del plan
        plan_map = {
            'mensual_nuevo_basico': 'Mensual Básico (Nuevo)',
            'anual_1_nuevo_basico': 'Anual 1 Básico (Nuevo)',
            'anual_2_nuevo_basico': 'Bianual Básico (Nuevo)',
            'mensual_basico': 'Mensual Básico',
            'anual_1_basico': 'Anual 1 Básico',
            'anual_2_basico': 'Bianual Básico',
            'mensual_nuevo_completo': 'Mensual Completo (Nuevo)',
            'anual_1_nuevo_completo': 'Anual 1 Completo (Nuevo)',
            'anual_2_nuevo_completo': 'Bianual Completo (Nuevo)',
            'mensual_completo': 'Mensual Completo',
            'anual_1_completo': 'Anual 1 Completo',
            'anual_2_completo': 'Bianual Completo',
        }
        return plan_map.get(obj.plan_seleccionado, obj.plan_seleccionado)
    plan_seleccionado_corto.short_description = 'Plan'
    plan_seleccionado_corto.admin_order_field = 'plan_seleccionado'

    def estado_badge(self, obj):
        colors = {
            'pendiente': '#ffc107',  # Amarillo
            'confirmado': '#28a745',  # Verde
            'rechazado': '#dc3545',   # Rojo
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado'

    def ver_comprobante(self, obj):
        if obj.comprobante:
            return format_html(
                '<a href="{}" target="_blank" style="color: #007bff;">📎 Ver Comprobante</a>',
                obj.comprobante.url
            )
        return '-'
    ver_comprobante.short_description = 'Comprobante'

    def confirmar_pagos_seleccionados(self, request, queryset):
        """Acción para confirmar múltiples pagos"""
        confirmados = 0
        for pago in queryset.filter(estado='pendiente'):
            if pago.confirmar_pago(usuario=request.user if hasattr(request.user, 'usuario') else None):
                confirmados += 1

        self.message_user(
            request,
            f'{confirmados} pago(s) confirmado(s) exitosamente. Las suscripciones han sido activadas.',
            level='success'
        )
    confirmar_pagos_seleccionados.short_description = '✅ Confirmar pagos seleccionados'

    def rechazar_pagos_seleccionados(self, request, queryset):
        """Acción para rechazar múltiples pagos"""
        rechazados = queryset.filter(estado='pendiente').update(estado='rechazado')

        self.message_user(
            request,
            f'{rechazados} pago(s) rechazado(s).',
            level='warning'
        )
    rechazar_pagos_seleccionados.short_description = '❌ Rechazar pagos seleccionados'

    def get_readonly_fields(self, request, obj=None):
        # Si el pago ya está confirmado o rechazado, hacer todos los campos readonly excepto notas_admin
        if obj and obj.estado in ['confirmado', 'rechazado']:
            return self.readonly_fields + ('empresa', 'monto', 'fecha_pago', 'metodo_pago',
                                          'plan_seleccionado', 'comprobante', 'referencia',
                                          'notas_cliente', 'estado')
        return self.readonly_fields
