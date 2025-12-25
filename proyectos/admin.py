from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    Cliente, Proveedor, Empleado, Proyecto, AsignacionEmpleado, Planilla,
    DetallePlanilla, Gasto, Pago, Usuario, OrdenCambio, Deduccion,
    Bonificacion, HoraExtra, HistorialSalario
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
