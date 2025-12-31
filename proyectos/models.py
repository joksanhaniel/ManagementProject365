from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from decimal import Decimal
import os
from django.utils.text import slugify


def gasto_upload_path(instance, filename):
    """
    Genera la ruta de subida de archivos para gastos, separando por empresa.

    Estructura: gastos/<empresa_codigo>/<proyecto_codigo>/<año>/<mes>/<filename>

    Ejemplo: gastos/empresa1/PROY001/2024/12/factura_materiales.pdf
    """
    # Obtener empresa y proyecto del gasto
    empresa_codigo = instance.proyecto.empresa.codigo if instance.proyecto.empresa else 'sin_empresa'
    proyecto_codigo = instance.proyecto.codigo

    # Obtener año y mes del gasto
    fecha = instance.fecha_gasto
    año = fecha.year
    mes = f"{fecha.month:02d}"

    # Limpiar el nombre del archivo
    nombre_base, extension = os.path.splitext(filename)
    nombre_limpio = slugify(nombre_base)
    filename_final = f"{nombre_limpio}{extension.lower()}"

    # Retornar ruta: gastos/empresa1/PROY001/2024/12/factura.pdf
    return f'gastos/{empresa_codigo}/{proyecto_codigo}/{año}/{mes}/{filename_final}'


def validar_tamanio_archivo(archivo):
    """
    Validador personalizado para verificar el tamaño del archivo.
    Límite: 10MB
    """
    max_size_mb = 10
    max_size_bytes = max_size_mb * 1024 * 1024

    if archivo.size > max_size_bytes:
        from django.core.exceptions import ValidationError
        raise ValidationError(f'El archivo no debe superar los {max_size_mb}MB. Tamaño actual: {archivo.size / (1024*1024):.2f}MB')


class EmpresaManager(models.Manager):
    """
    Manager personalizado que filtra automáticamente por empresa.
    Solo se usa cuando hay una empresa en el contexto (request).
    """
    def __init__(self, *args, **kwargs):
        self.empresa_id = None
        super().__init__(*args, **kwargs)

    def for_empresa(self, empresa):
        """Filtra los objetos por empresa"""
        if empresa:
            return self.filter(empresa=empresa)
        return self.none()

    def get_queryset(self):
        """
        Retorna el queryset base. El filtrado por empresa se hace
        manualmente en las vistas usando for_empresa().
        """
        return super().get_queryset()


class Empresa(models.Model):
    """
    Modelo para gestión de múltiples empresas en el sistema.
    Cada empresa tiene sus propios proyectos, clientes, empleados, etc.
    """
    nombre = models.CharField(max_length=200, unique=True, verbose_name='Nombre Comercial',
                             help_text='Nombre único que identifica la empresa')
    codigo = models.CharField(max_length=200, unique=True, editable=False, verbose_name='Código',
                             help_text='Código generado automáticamente del nombre (se usa en URLs)')
    razon_social = models.CharField(max_length=200, verbose_name='Razón Social')
    rtn = models.CharField(max_length=14, unique=True, verbose_name='RTN')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, null=True, verbose_name='Correo Electrónico')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    logo = models.ImageField(upload_to='empresas/logos/', blank=True, null=True, verbose_name='Logo')
    activa = models.BooleanField(default=True, verbose_name='Empresa Activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última Modificación')

    # Campos de Suscripción SaaS
    TIPO_SUSCRIPCION_CHOICES = [
        ('trial', 'Trial (15 días gratis)'),
        ('mensual', 'Plan Mensual'),
        ('anual', 'Plan Anual'),
    ]

    ESTADO_SUSCRIPCION_CHOICES = [
        ('trial', 'En Trial'),
        ('activa', 'Activa'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]

    tipo_suscripcion = models.CharField(
        max_length=20,
        choices=TIPO_SUSCRIPCION_CHOICES,
        default='trial',
        verbose_name='Tipo de Suscripción'
    )
    estado_suscripcion = models.CharField(
        max_length=20,
        choices=ESTADO_SUSCRIPCION_CHOICES,
        default='trial',
        verbose_name='Estado de Suscripción'
    )
    fecha_inicio_suscripcion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha Inicio de Suscripción'
    )
    fecha_expiracion_suscripcion = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Expiración'
    )
    cuota_instalacion_pagada = models.BooleanField(
        default=False,
        verbose_name='Cuota de Instalación Pagada'
    )
    plan_incluye_maquinaria = models.BooleanField(
        default=True,
        verbose_name='Plan Incluye Módulo de Maquinaria',
        help_text='Plan Completo incluye gestión de maquinaria. Plan Básico no incluye este módulo.'
    )
    plan_elegido = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Plan Elegido al Registrarse',
        help_text='Plan que el cliente seleccionó al momento del registro (se activa cuando paga)',
        choices=[
            ('mensual_nuevo_basico', 'Plan Mensual Básico'),
            ('anual_1_nuevo_basico', 'Plan Anual Básico (1 año)'),
            ('anual_2_nuevo_basico', 'Plan Bianual Básico (2 años)'),
            ('mensual_nuevo_completo', 'Plan Mensual Completo'),
            ('anual_1_nuevo_completo', 'Plan Anual Completo (1 año)'),
            ('anual_2_nuevo_completo', 'Plan Bianual Completo (2 años)'),
        ]
    )

    # Campos de seguridad para prevenir abuso de trials
    ip_registro = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='IP de Registro',
        help_text='IP desde donde se registró la empresa'
    )

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        """Genera automáticamente el código a partir del nombre"""
        if not self.codigo or self.has_nombre_changed():
            import re
            codigo = self.nombre.upper()
            codigo = re.sub(r'[^\w\s-]', '', codigo)  # Eliminar caracteres especiales
            codigo = re.sub(r'[-\s]+', '-', codigo)    # Reemplazar espacios con guiones
            self.codigo = codigo.strip('-')
        super().save(*args, **kwargs)

    def has_nombre_changed(self):
        """Verifica si el nombre ha cambiado"""
        if not self.pk:
            return True
        try:
            old = Empresa.objects.get(pk=self.pk)
            return old.nombre != self.nombre
        except Empresa.DoesNotExist:
            return True

    def get_url_prefix(self):
        """Retorna el prefijo de URL para esta empresa"""
        return self.codigo

    def iniciar_trial(self):
        """
        Inicia el período de trial de 15 días.
        El trial SIEMPRE incluye TODOS los módulos (incluyendo maquinaria)
        para que el cliente pueda probar el sistema completo.
        """
        from datetime import date, timedelta
        self.tipo_suscripcion = 'trial'
        self.estado_suscripcion = 'trial'
        self.fecha_inicio_suscripcion = date.today()
        self.fecha_expiracion_suscripcion = date.today() + timedelta(days=15)
        self.plan_incluye_maquinaria = True  # Trial SIEMPRE con todos los módulos
        self.save()

    def activar_suscripcion(self, tipo='mensual', duracion_dias=30):
        """
        Activa una suscripción pagada
        tipo: 'mensual', 'anual'
        duracion_dias: días de duración (30 para mensual, 330 para anual 11 meses, 690 para bianual 23 meses)
        """
        from datetime import date, timedelta
        self.tipo_suscripcion = tipo
        self.estado_suscripcion = 'activa'
        self.fecha_inicio_suscripcion = date.today()
        self.fecha_expiracion_suscripcion = date.today() + timedelta(days=duracion_dias)
        self.save()

    def esta_en_trial(self):
        """Verifica si la empresa está en período de trial"""
        return self.estado_suscripcion == 'trial'

    def suscripcion_activa(self):
        """Verifica si la suscripción está activa (trial o pagada)"""
        from datetime import date
        if not self.fecha_expiracion_suscripcion:
            return False
        return self.estado_suscripcion in ['trial', 'activa'] and self.fecha_expiracion_suscripcion >= date.today()

    def suscripcion_vencida(self):
        """Verifica si la suscripción está vencida"""
        from datetime import date
        if not self.fecha_expiracion_suscripcion:
            return True
        return self.fecha_expiracion_suscripcion < date.today()

    def dias_restantes(self):
        """Retorna los días restantes de la suscripción"""
        from datetime import date
        if not self.fecha_expiracion_suscripcion:
            return 0
        delta = self.fecha_expiracion_suscripcion - date.today()
        return max(0, delta.days)

    def puede_crear_registros(self):
        """Verifica si la empresa puede crear nuevos registros (no está en trial o tiene suscripción activa)"""
        return self.estado_suscripcion == 'activa' and self.suscripcion_activa()


class Plan(models.Model):
    """
    Modelo para los planes de suscripción disponibles
    """
    TIPO_PLAN_CHOICES = [
        ('setup', 'Cuota de Instalación (Una vez)'),
        ('mensual', 'Plan Mensual'),
        ('anual', 'Plan Anual'),
    ]

    nombre = models.CharField(max_length=100, verbose_name='Nombre del Plan')
    tipo = models.CharField(max_length=20, choices=TIPO_PLAN_CHOICES, verbose_name='Tipo de Plan')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio (L.)')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Plan Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Plan de Suscripción'
        verbose_name_plural = 'Planes de Suscripción'
        ordering = ['tipo', 'precio']

    def __str__(self):
        return f"{self.nombre} - L. {self.precio}"


class HistorialPago(models.Model):
    """
    Modelo para registrar historial de pagos de suscripciones
    """
    METODO_PAGO_CHOICES = [
        ('transferencia_bac', 'Transferencia BAC'),
        ('transferencia_occidente', 'Transferencia Banco de Occidente'),
        ('deposito_bac', 'Depósito en efectivo BAC'),
        ('deposito_occidente', 'Depósito en efectivo Occidente'),
        ('cheque', 'Cheque'),
        ('otro', 'Otro'),
    ]

    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente de Verificación'),
        ('verificado', 'Verificado y Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    empresa = models.ForeignKey('Empresa', on_delete=models.PROTECT, related_name='pagos', verbose_name='Empresa')
    plan = models.ForeignKey('Plan', on_delete=models.PROTECT, verbose_name='Plan Pagado')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto Pagado (L.)')
    metodo_pago = models.CharField(max_length=30, choices=METODO_PAGO_CHOICES, verbose_name='Método de Pago')
    numero_referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de Referencia/Comprobante')
    comprobante = models.ImageField(upload_to='pagos/comprobantes/', blank=True, null=True, verbose_name='Comprobante de Pago')
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente', verbose_name='Estado del Pago')
    fecha_pago = models.DateField(verbose_name='Fecha del Pago')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    fecha_verificacion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Verificación')
    verificado_por = models.ForeignKey('Usuario', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Verificado por')
    notas = models.TextField(blank=True, null=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Historial de Pago'
        verbose_name_plural = 'Historial de Pagos'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"{self.empresa.nombre} - {self.plan.nombre} - L. {self.monto} ({self.get_estado_display()})"


class RegistroTrial(models.Model):
    """
    Modelo para rastrear registros de trials y prevenir abusos.
    Permite detectar múltiples registros desde la misma IP o email.
    """
    ip_address = models.GenericIPAddressField(verbose_name='Dirección IP')
    email_empresa = models.EmailField(verbose_name='Email de Empresa')
    email_usuario = models.EmailField(verbose_name='Email de Usuario')
    rtn = models.CharField(max_length=14, verbose_name='RTN')
    empresa_creada = models.ForeignKey('Empresa', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Empresa Creada')
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    bloqueado = models.BooleanField(default=False, verbose_name='Bloqueado')
    motivo_bloqueo = models.TextField(blank=True, null=True, verbose_name='Motivo de Bloqueo')

    class Meta:
        verbose_name = 'Registro de Trial'
        verbose_name_plural = 'Registros de Trials'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['email_empresa']),
            models.Index(fields=['fecha_registro']),
        ]

    def __str__(self):
        return f"{self.email_empresa} - {self.ip_address} ({self.fecha_registro.strftime('%d/%m/%Y %H:%M')})"

    @staticmethod
    def contar_registros_recientes_ip(ip_address, dias=30):
        """Cuenta cuántos registros ha hecho esta IP en los últimos N días"""
        from datetime import timedelta
        from django.utils import timezone
        fecha_limite = timezone.now() - timedelta(days=dias)
        return RegistroTrial.objects.filter(
            ip_address=ip_address,
            fecha_registro__gte=fecha_limite
        ).count()

    @staticmethod
    def contar_registros_recientes_email(email, dias=30):
        """Cuenta cuántos registros ha hecho este email en los últimos N días"""
        from datetime import timedelta
        from django.utils import timezone
        fecha_limite = timezone.now() - timedelta(days=dias)
        return RegistroTrial.objects.filter(
            models.Q(email_empresa=email) | models.Q(email_usuario=email),
            fecha_registro__gte=fecha_limite
        ).count()

    @staticmethod
    def esta_ip_bloqueada(ip_address):
        """Verifica si esta IP está bloqueada"""
        return RegistroTrial.objects.filter(ip_address=ip_address, bloqueado=True).exists()

    @staticmethod
    def validar_nuevo_registro(ip_address, email_empresa, email_usuario, limite_ip=3, limite_email=2):
        """
        Valida si se puede permitir un nuevo registro.
        Retorna (puede_registrar, mensaje_error)
        """
        # Verificar si la IP está bloqueada
        if RegistroTrial.esta_ip_bloqueada(ip_address):
            return False, "Tu dirección IP ha sido bloqueada. Contacta al soporte."

        # Verificar límite de registros por IP
        registros_ip = RegistroTrial.contar_registros_recientes_ip(ip_address, dias=30)
        if registros_ip >= limite_ip:
            return False, f"Has excedido el límite de {limite_ip} registros de prueba por mes. Si necesitas ayuda, contáctanos."

        # Verificar límite de registros por email de empresa
        registros_email_empresa = RegistroTrial.contar_registros_recientes_email(email_empresa, dias=30)
        if registros_email_empresa >= limite_email:
            return False, "Este email ya ha sido usado para registros de prueba. Usa un email diferente o contacta al soporte."

        # Verificar límite de registros por email de usuario
        registros_email_usuario = RegistroTrial.contar_registros_recientes_email(email_usuario, dias=30)
        if registros_email_usuario >= limite_email:
            return False, "Este email ya ha sido usado para registros de prueba. Usa un email diferente o contacta al soporte."

        return True, None


class Cliente(models.Model):
    empresa = models.ForeignKey('Empresa', on_delete=models.PROTECT, related_name='clientes', verbose_name='Empresa', null=True, blank=True)
    codigo = models.CharField(max_length=20, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre o Razón Social')
    rtn = models.CharField(max_length=14, verbose_name='RTN')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, null=True, verbose_name='Correo Electrónico')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    contacto = models.CharField(max_length=200, blank=True, null=True, verbose_name='Persona de Contacto')
    activo = models.BooleanField(default=True)

    objects = EmpresaManager()

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
        unique_together = [['empresa', 'codigo'], ['empresa', 'rtn']]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Proveedor(models.Model):
    empresa = models.ForeignKey('Empresa', on_delete=models.PROTECT, related_name='proveedores', verbose_name='Empresa', null=True, blank=True)
    codigo = models.CharField(max_length=20, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre o Razón Social')
    rtn = models.CharField(max_length=14, verbose_name='RTN')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, null=True, verbose_name='Correo Electrónico')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    contacto = models.CharField(max_length=200, blank=True, null=True, verbose_name='Persona de Contacto')
    tipo_proveedor = models.CharField(max_length=50, blank=True, null=True, verbose_name='Tipo de Proveedor',
                                      help_text='Ej: Materiales, Equipos, Servicios, etc.')
    activo = models.BooleanField(default=True)

    objects = EmpresaManager()

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
        unique_together = [['empresa', 'codigo'], ['empresa', 'rtn']]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Empleado(models.Model):
    TIPO_CONTRATO_CHOICES = [
        ('permanente', 'Permanente'),
        ('temporal', 'Temporal'),
        ('subcontratista', 'Subcontratista'),
    ]

    empresa = models.ForeignKey('Empresa', on_delete=models.PROTECT, related_name='empleados', verbose_name='Empresa', null=True, blank=True)
    codigo = models.CharField(max_length=20, verbose_name='Código')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, verbose_name='DNI')
    rtn = models.CharField(max_length=20, blank=True, null=True, verbose_name='RTN')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    cargo = models.CharField(max_length=100)
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, default='temporal')
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Salario Base')
    fecha_ingreso = models.DateField()
    activo = models.BooleanField(default=True)

    objects = EmpresaManager()

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['apellidos', 'nombres']
        unique_together = [['empresa', 'codigo'], ['empresa', 'dni']]

    def __str__(self):
        return f"{self.codigo} - {self.nombres} {self.apellidos}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ('planificacion', 'Planificación'),
        ('en_progreso', 'En Progreso'),
        ('suspendido', 'Suspendido'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    empresa = models.ForeignKey('Empresa', on_delete=models.PROTECT, related_name='proyectos', verbose_name='Empresa', null=True, blank=True)
    codigo = models.CharField(max_length=20, verbose_name='Código')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='proyectos', verbose_name='Cliente', blank=True, null=True)
    direccion = models.TextField(verbose_name='Dirección del Proyecto')
    monto_contrato = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Monto del Contrato')
    fecha_inicio = models.DateField()
    fecha_fin_estimada = models.DateField(verbose_name='Fecha Fin Estimada')
    fecha_fin_real = models.DateField(blank=True, null=True, verbose_name='Fecha Fin Real')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='planificacion')
    porcentaje_avance = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))], verbose_name='% Avance')

    objects = EmpresaManager()

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-fecha_inicio']
        unique_together = [['empresa', 'codigo']]

    def __str__(self):
        if self.cliente:
            return f"{self.codigo} - {self.nombre} ({self.cliente.nombre})"
        return f"{self.codigo} - {self.nombre}"

    def calcular_costos_totales(self):
        """Calcula el total de costos del proyecto (planilla + gastos + maquinaria)"""
        total_planilla = sum(p.monto_total for p in self.planillas.all())
        total_gastos = sum(g.monto for g in self.gastos.all())
        total_maquinaria = sum(uso.costo_total for uso in self.usos_maquinaria.all())
        return total_planilla + total_gastos + total_maquinaria

    def calcular_costo_maquinaria(self):
        """Calcula el total de costos de maquinaria del proyecto"""
        return sum(uso.costo_total for uso in self.usos_maquinaria.all())

    def calcular_utilidad_bruta(self):
        """Calcula la utilidad bruta (monto contrato - costos totales)"""
        return self.monto_contrato - self.calcular_costos_totales()

    def calcular_margen_utilidad(self):
        """Calcula el margen de utilidad en porcentaje"""
        if self.monto_contrato > 0:
            return (self.calcular_utilidad_bruta() / self.monto_contrato) * 100
        return 0

    def calcular_total_ordenes_cambio(self):
        """Calcula el total de órdenes de cambio aprobadas"""
        return sum(
            oc.monto_adicional
            for oc in self.ordenes_cambio.filter(estado__in=['aprobada', 'en_ejecucion', 'completada'])
        )

    def calcular_monto_total_proyecto(self):
        """Calcula el monto total del proyecto (contrato original + órdenes de cambio)"""
        return self.monto_contrato + self.calcular_total_ordenes_cambio()

    def calcular_total_pagado(self):
        """Calcula el total pagado por el cliente (desembolsos)"""
        return sum(p.monto for p in self.pagos.all())

    def calcular_saldo_pendiente(self):
        """Calcula cuánto falta por pagar del monto total del proyecto"""
        return self.calcular_monto_total_proyecto() - self.calcular_total_pagado()

    def calcular_porcentaje_pagado(self):
        """Calcula el porcentaje pagado del monto total"""
        monto_total = self.calcular_monto_total_proyecto()
        if monto_total > 0:
            return (self.calcular_total_pagado() / monto_total) * 100
        return 0


class AsignacionEmpleado(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='asignaciones')
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='asignaciones')
    fecha_asignacion = models.DateField(verbose_name='Fecha Asignación')
    fecha_finalizacion = models.DateField(blank=True, null=True, verbose_name='Fecha Finalización')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Asignación de Empleado'
        verbose_name_plural = 'Asignaciones de Empleados'
        unique_together = ['proyecto', 'empleado', 'fecha_asignacion']
        ordering = ['-fecha_asignacion']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.proyecto.nombre}"


class Planilla(models.Model):
    TIPO_PLANILLA_CHOICES = [
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
        ('semanal', 'Semanal'),
    ]

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='planillas')
    periodo_inicio = models.DateField(verbose_name='Período Inicio')
    periodo_fin = models.DateField(verbose_name='Período Fin')
    tipo_planilla = models.CharField(max_length=20, choices=TIPO_PLANILLA_CHOICES, default='quincenal')
    fecha_pago = models.DateField(verbose_name='Fecha de Pago')
    observaciones = models.TextField(blank=True, null=True)
    pagada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Planilla'
        verbose_name_plural = 'Planillas'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"Planilla {self.proyecto.codigo} - {self.periodo_inicio} a {self.periodo_fin}"

    @property
    def monto_total(self):
        """Calcula el monto total de la planilla"""
        return sum(d.calcular_total() for d in self.detalles.all())


class DetallePlanilla(models.Model):
    planilla = models.ForeignKey(Planilla, on_delete=models.CASCADE, related_name='detalles')
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    salario_devengado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Salario Devengado', editable=False)

    class Meta:
        verbose_name = 'Detalle de Planilla'
        verbose_name_plural = 'Detalles de Planilla'
        unique_together = ['planilla', 'empleado']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.planilla}"

    def save(self, *args, **kwargs):
        """Auto-calcular salario_devengado basado en el tipo de planilla"""
        if not self.salario_devengado or self.salario_devengado == 0:
            if self.empleado and self.planilla:
                if self.planilla.tipo_planilla == 'semanal':
                    # Salario mensual / 4 semanas
                    self.salario_devengado = self.empleado.salario_base / 4
                elif self.planilla.tipo_planilla == 'quincenal':
                    # Salario mensual / 2 quincenas
                    self.salario_devengado = self.empleado.salario_base / 2
                elif self.planilla.tipo_planilla == 'mensual':
                    # Salario completo
                    self.salario_devengado = self.empleado.salario_base
        super().save(*args, **kwargs)

    def calcular_total_deducciones(self):
        """Calcula el total de deducciones registradas para este empleado en esta planilla"""
        from django.db.models import Sum
        total = Deduccion.objects.filter(
            planilla=self.planilla,
            empleado=self.empleado
        ).aggregate(total=Sum('monto'))['total'] or 0
        return total

    def calcular_total_bonificaciones(self):
        """Calcula el total de bonificaciones registradas para este empleado en esta planilla"""
        from django.db.models import Sum
        total = Bonificacion.objects.filter(
            planilla=self.planilla,
            empleado=self.empleado
        ).aggregate(total=Sum('monto'))['total'] or 0
        return total

    def calcular_total_horas_extra(self):
        """Calcula el total de horas extra (cantidad) registradas para este empleado en esta planilla"""
        from django.db.models import Sum
        total_horas = HoraExtra.objects.filter(
            planilla=self.planilla,
            empleado=self.empleado
        ).aggregate(total=Sum('cantidad_horas'))['total'] or 0
        return total_horas

    def calcular_monto_horas_extra(self):
        """Calcula el monto total de horas extra registradas para este empleado en esta planilla"""
        from django.db.models import Sum
        total_monto = HoraExtra.objects.filter(
            planilla=self.planilla,
            empleado=self.empleado
        ).aggregate(total=Sum('monto'))['total'] or 0
        return total_monto

    def calcular_total(self):
        """
        Calcula el total a pagar al empleado.
        Total = Salario Devengado + Bonificaciones + Monto Horas Extra - Deducciones
        """
        total_deducciones = self.calcular_total_deducciones()
        total_bonificaciones = self.calcular_total_bonificaciones()
        monto_horas_extra = self.calcular_monto_horas_extra()

        return self.salario_devengado + total_bonificaciones + monto_horas_extra - total_deducciones


class Gasto(models.Model):
    TIPO_GASTO_CHOICES = [
        ('materiales', 'Materiales'),
        ('equipo', 'Equipo'),
        ('servicios', 'Servicios'),
        ('transporte', 'Transporte'),
        ('otros', 'Otros'),
    ]

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='gastos')
    tipo_gasto = models.CharField(max_length=20, choices=TIPO_GASTO_CHOICES)
    descripcion = models.TextField(verbose_name='Descripción')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='gastos')
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    fecha_gasto = models.DateField()
    numero_factura = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número de Factura')
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(blank=True, null=True, verbose_name='Fecha de Pago')

    # Campo para adjuntar factura o documento
    archivo_adjunto = models.FileField(
        upload_to=gasto_upload_path,
        blank=True,
        null=True,
        verbose_name='Factura/Documento Adjunto',
        help_text='Adjuntar factura, recibo o documento relacionado (PDF, Imagen, Excel). Máximo 10MB.',
        validators=[
            validar_tamanio_archivo,
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'xlsx', 'xls', 'doc', 'docx'],
                message='Solo se permiten archivos PDF, imágenes (JPG, PNG), Excel o Word.'
            )
        ]
    )

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-fecha_gasto']

    def __str__(self):
        return f"{self.proyecto.codigo} - {self.descripcion[:50]} - ${self.monto}"

    def get_nombre_archivo(self):
        """Retorna solo el nombre del archivo sin la ruta completa"""
        if self.archivo_adjunto:
            return os.path.basename(self.archivo_adjunto.name)
        return None

    def get_extension_archivo(self):
        """Retorna la extensión del archivo en minúsculas"""
        if self.archivo_adjunto:
            return os.path.splitext(self.archivo_adjunto.name)[1].lower().replace('.', '')
        return None


class Pago(models.Model):
    """
    Desembolsos o pagos parciales que el cliente realiza del monto total del contrato.
    Los clientes generalmente no pagan todo de una vez sino por partes.
    """
    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
        ('deposito', 'Depósito'),
    ]

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='pagos')
    concepto = models.CharField(max_length=200, blank=True, null=True, verbose_name='Concepto del Pago')
    monto = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Monto del Desembolso')
    fecha_pago = models.DateField(verbose_name='Fecha del Desembolso')
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES)
    numero_referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name='Número de Referencia')
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Pago Recibido (Desembolso)'
        verbose_name_plural = 'Pagos Recibidos (Desembolsos)'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"{self.proyecto.codigo} - ${self.monto} - {self.fecha_pago}"


class OrdenCambio(models.Model):
    """
    Trabajos adicionales o cambios solicitados durante el proyecto que implican
    un costo adicional al monto original del contrato.
    Ejemplo: cambiar una pared, agregar una habitación, etc.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente Aprobación'),
        ('aprobada', 'Aprobada'),
        ('en_ejecucion', 'En Ejecución'),
        ('completada', 'Completada'),
        ('rechazada', 'Rechazada'),
    ]

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='ordenes_cambio')
    codigo = models.CharField(max_length=20, verbose_name='Código OC')
    descripcion = models.TextField(verbose_name='Descripción del Cambio')
    monto_adicional = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Monto Adicional')
    fecha_solicitud = models.DateField(verbose_name='Fecha de Solicitud')
    fecha_aprobacion = models.DateField(blank=True, null=True, verbose_name='Fecha de Aprobación')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    solicitado_por = models.CharField(max_length=200, blank=True, null=True, verbose_name='Solicitado Por', help_text='Cliente o responsable')
    justificacion = models.TextField(blank=True, null=True, verbose_name='Justificación')
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Orden de Cambio'
        verbose_name_plural = 'Órdenes de Cambio'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.codigo} - {self.proyecto.codigo} - ${self.monto_adicional}"


class Usuario(AbstractUser):
    """
    Usuario personalizado con roles y permisos específicos para el sistema MultiProject Pro.

    Roles disponibles:
    - Gerente: Acceso total a la aplicación web (sin acceso a Django Admin)
    - Supervisor: Gestión de proyectos, empleados, planillas y gastos
    - Contador: Acceso a información financiera, planillas y gastos
    - Auxiliar: Gestión de asignaciones y consulta de proyectos
    - Operador: Acceso a gastos y maquinaria
    - Usuario: Solo lectura de proyectos y reportes

    Nota: El superusuario (is_superuser=True) tiene acceso completo al sistema incluyendo Django Admin
    """

    ROL_CHOICES = [
        ('gerente', 'Gerente'),
        ('supervisor', 'Supervisor'),
        ('contador', 'Contador'),
        ('auxiliar', 'Auxiliar'),
        ('operador', 'Operador'),
        ('usuario', 'Usuario'),
    ]

    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.PROTECT,
        related_name='usuarios',
        null=True,
        blank=True,
        verbose_name='Empresa',
        help_text='Empresa a la que pertenece el usuario. Superusuarios pueden no tener empresa asignada.'
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='usuario',
        verbose_name='Rol'
    )
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    activo = models.BooleanField(default=True, verbose_name='Usuario Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última Modificación')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Asignar grupo según el rol
        if is_new or 'rol' in kwargs.get('update_fields', []):
            self.groups.clear()
            group_name = self.get_group_name()
            group, _ = Group.objects.get_or_create(name=group_name)
            self.groups.add(group)

    def get_group_name(self):
        """Retorna el nombre del grupo según el rol"""
        group_mapping = {
            'gerente': 'Gerentes',
            'supervisor': 'Supervisores',
            'contador': 'Contadores',
            'auxiliar': 'Auxiliares',
            'operador': 'Operadores',
            'usuario': 'Usuarios',
        }
        return group_mapping.get(self.rol, 'Usuarios')

    def tiene_permiso_escritura(self):
        """Verifica si el usuario puede crear/editar/eliminar"""
        return self.is_superuser or self.rol in ['gerente', 'supervisor']

    def tiene_permiso_financiero(self):
        """Verifica si el usuario tiene acceso a información financiera"""
        return self.is_superuser or self.rol in ['gerente', 'supervisor', 'contador']

    def tiene_permiso_planillas(self):
        """Verifica si el usuario puede gestionar planillas"""
        return self.is_superuser or self.rol in ['gerente', 'supervisor', 'contador']

    def tiene_permiso_empleados(self):
        """Verifica si el usuario puede gestionar empleados"""
        return self.is_superuser or self.rol in ['gerente', 'supervisor', 'auxiliar']


class Deduccion(models.Model):
    """
    Deducciones aplicadas a empleados en una planilla.
    Sistema simplificado para registrar cualquier tipo de deducción.
    """
    planilla = models.ForeignKey(
        Planilla,
        on_delete=models.CASCADE,
        related_name='deducciones',
        verbose_name='Planilla'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='deducciones',
        verbose_name='Empleado'
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name='Descripción',
        help_text='Ej: IHSS, ISR, Préstamo, Anticipo, etc.'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto a Deducir'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Deducción'
        verbose_name_plural = 'Deducciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.descripcion} - L. {self.monto}"


class Bonificacion(models.Model):
    """
    Bonificaciones aplicadas a empleados en una planilla.
    Sistema simplificado para registrar cualquier tipo de bonificación.
    """
    planilla = models.ForeignKey(
        Planilla,
        on_delete=models.CASCADE,
        related_name='bonificaciones',
        verbose_name='Planilla'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='bonificaciones',
        verbose_name='Empleado'
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name='Descripción',
        help_text='Ej: Bono por rendimiento, Incentivo, etc.'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto de Bonificación'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Bonificación'
        verbose_name_plural = 'Bonificaciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.descripcion} - L. {self.monto}"


class HoraExtra(models.Model):
    """
    Horas extra trabajadas por empleados en una planilla.
    Sistema simplificado para registrar horas extra.
    """
    planilla = models.ForeignKey(
        Planilla,
        on_delete=models.CASCADE,
        related_name='horas_extra',
        verbose_name='Planilla'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='horas_extra',
        verbose_name='Empleado'
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name='Descripción',
        help_text='Ej: Horas extra nocturnas, Horas extra domingo, etc.'
    )
    cantidad_horas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Cantidad de Horas'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto a Pagar'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Hora Extra'
        verbose_name_plural = 'Horas Extra'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.cantidad_horas} hrs - L. {self.monto}"


class HistorialSalario(models.Model):
    """
    Modelo para llevar un historial de cambios en el salario base de los empleados.
    Se crea automáticamente cuando se modifica el salario_base de un empleado.
    """
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='historial_salarios',
        verbose_name='Empleado'
    )
    salario_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Salario Anterior',
        null=True,
        blank=True
    )
    salario_nuevo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Salario Nuevo'
    )
    fecha_cambio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del Cambio'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cambios_salario_realizados',
        verbose_name='Usuario que Realizó el Cambio'
    )
    motivo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Motivo del Cambio',
        help_text='Ej: Aumento anual, Promoción, Ajuste por inflación, etc.'
    )

    def __str__(self):
        if self.salario_anterior:
            return f"{self.empleado.nombre_completo}: L.{self.salario_anterior} → L.{self.salario_nuevo} ({self.fecha_cambio.strftime('%d/%m/%Y')})"
        else:
            return f"{self.empleado.nombre_completo}: Salario inicial L.{self.salario_nuevo} ({self.fecha_cambio.strftime('%d/%m/%Y')})"

    class Meta:
        verbose_name = 'Historial de Salario'
        verbose_name_plural = 'Historial de Salarios'
        ordering = ['-fecha_cambio']


# ====== MODELOS DE MAQUINARIA ======

class Maquinaria(models.Model):
    """Catálogo de maquinaria disponible para usar en proyectos"""
    TIPO_CHOICES = [
        ('retroexcavadora', 'Retroexcavadora'),
        ('excavadora', 'Excavadora'),
        ('bulldozer', 'Bulldozer'),
        ('camion', 'Camión'),
        ('grua', 'Grúa'),
        ('compactadora', 'Compactadora'),
        ('motoniveladora', 'Motoniveladora'),
        ('cargador', 'Cargador Frontal'),
        ('vibrador', 'Vibrador'),
        ('otro', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_uso', 'En Uso'),
        ('mantenimiento', 'Mantenimiento'),
        ('fuera_servicio', 'Fuera de Servicio'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='maquinarias', verbose_name='Empresa')
    codigo = models.CharField(max_length=20, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre/Descripción')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Tipo de Maquinaria')
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name='Marca')
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Modelo')
    placa = models.CharField(max_length=20, blank=True, null=True, verbose_name='Placa/Matrícula')

    # Horómetro
    horometro_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Horómetro Actual (horas)',
        help_text='Horas acumuladas de uso de la maquinaria'
    )

    # Tarifas
    tarifa_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Tarifa por Hora',
        help_text='Costo por hora de uso'
    )

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible', verbose_name='Estado')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última Modificación')

    class Meta:
        verbose_name = 'Maquinaria'
        verbose_name_plural = 'Maquinarias'
        ordering = ['codigo']
        unique_together = ['empresa', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class UsoMaquinaria(models.Model):
    """Registro de uso de maquinaria en un proyecto"""
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='usos_maquinaria',
        verbose_name='Proyecto'
    )
    maquinaria = models.ForeignKey(
        Maquinaria,
        on_delete=models.PROTECT,
        related_name='usos',
        verbose_name='Maquinaria'
    )

    # Registro de horómetros
    fecha_inicio = models.DateField(verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de Fin')

    horometro_inicial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Horómetro Inicial',
        help_text='Lectura del horómetro al iniciar'
    )
    horometro_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Horómetro Final',
        help_text='Lectura del horómetro al finalizar'
    )

    # Tarifa aplicada (puede ser diferente a la tarifa actual)
    tarifa_aplicada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Tarifa Aplicada (por hora)'
    )

    # Operador (opcional) - Usuario con rol operador que opera la maquinaria
    operador = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'operador'},
        related_name='usos_maquinaria_operados',
        verbose_name='Operador'
    )

    descripcion_trabajo = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción del Trabajo Realizado'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última Modificación')

    class Meta:
        verbose_name = 'Uso de Maquinaria'
        verbose_name_plural = 'Usos de Maquinaria'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.maquinaria.codigo} - {self.proyecto.codigo} ({self.fecha_inicio})"

    @property
    def horas_trabajadas(self):
        """Calcula las horas trabajadas"""
        if self.horometro_final and self.horometro_inicial:
            return self.horometro_final - self.horometro_inicial
        return Decimal('0.00')

    @property
    def costo_total(self):
        """Calcula el costo total del uso"""
        return self.horas_trabajadas * self.tarifa_aplicada

    def save(self, *args, **kwargs):
        # Auto-asignar tarifa si no se especificó
        if not self.tarifa_aplicada:
            self.tarifa_aplicada = self.maquinaria.tarifa_hora

        # Gestión automática del estado de la maquinaria
        is_new = self.pk is None

        if is_new:
            # Si es un nuevo uso, marcar la maquinaria como "en_uso"
            self.maquinaria.estado = 'en_uso'
            self.maquinaria.save(update_fields=['estado'])

        # Si el uso se finaliza (tiene fecha_fin y horometro_final)
        if self.fecha_fin and self.horometro_final:
            # Actualizar horómetro de la maquinaria
            self.maquinaria.horometro_actual = self.horometro_final
            # Marcar como disponible si no hay otros usos activos
            otros_usos_activos = UsoMaquinaria.objects.filter(
                maquinaria=self.maquinaria,
                fecha_fin__isnull=True
            ).exclude(pk=self.pk).exists()

            if not otros_usos_activos:
                self.maquinaria.estado = 'disponible'

            self.maquinaria.save(update_fields=['horometro_actual', 'estado'])

        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError

        # Validar que horómetro final sea mayor que inicial
        if self.horometro_final and self.horometro_inicial:
            if self.horometro_final <= self.horometro_inicial:
                raise ValidationError({
                    'horometro_final': 'El horómetro final debe ser mayor al inicial'
                })

        # Si estamos editando (self.pk existe)
        if self.pk:
            # Obtener el objeto original de la base de datos
            try:
                original = UsoMaquinaria.objects.get(pk=self.pk)

                # Si el uso ya está finalizado, NO permitir edición
                if original.fecha_fin and original.horometro_final:
                    raise ValidationError(
                        'No se puede editar un uso de maquinaria que ya está finalizado. '
                        'El uso fue completado y cerrado.'
                    )
            except UsoMaquinaria.DoesNotExist:
                pass

            # Validar que no afecte registros posteriores
            if self.horometro_final:
                usos_posteriores = UsoMaquinaria.objects.filter(
                    maquinaria=self.maquinaria,
                    fecha_inicio__gt=self.fecha_inicio
                ).exclude(pk=self.pk).order_by('fecha_inicio').first()

                if usos_posteriores:
                    # Validar que nuestro horómetro final no sea mayor al inicial del siguiente
                    if self.horometro_final > usos_posteriores.horometro_inicial:
                        raise ValidationError({
                            'horometro_final': f'El horómetro final no puede ser mayor a {usos_posteriores.horometro_inicial} hrs (horómetro inicial del uso posterior del {usos_posteriores.fecha_inicio.strftime("%d/%m/%Y")})'
                        })

        # Solo validar horómetro inicial y estado de maquinaria en creación (no en edición)
        if not self.pk:
            # Validar que la maquinaria no esté en uso
            if self.maquinaria.estado == 'en_uso':
                # Buscar el uso activo
                uso_activo = UsoMaquinaria.objects.filter(
                    maquinaria=self.maquinaria,
                    fecha_fin__isnull=True
                ).first()

                if uso_activo:
                    raise ValidationError({
                        'maquinaria': f'La maquinaria está actualmente en uso en el proyecto "{uso_activo.proyecto.nombre}" desde el {uso_activo.fecha_inicio.strftime("%d/%m/%Y")}. Debe finalizar ese uso antes de crear uno nuevo.'
                    })

            # Validar que la maquinaria no esté en mantenimiento o fuera de servicio
            if self.maquinaria.estado == 'mantenimiento':
                raise ValidationError({
                    'maquinaria': 'La maquinaria está en mantenimiento y no puede ser utilizada.'
                })
            elif self.maquinaria.estado == 'fuera_servicio':
                raise ValidationError({
                    'maquinaria': 'La maquinaria está fuera de servicio y no puede ser utilizada.'
                })
            # Determinar el horómetro mínimo permitido
            horometro_minimo = self.maquinaria.horometro_actual

            # Validar que el horómetro inicial no sea menor al último horómetro final registrado
            ultimo_uso = UsoMaquinaria.objects.filter(
                maquinaria=self.maquinaria
            ).exclude(pk=self.pk).order_by('-horometro_final').first()

            if ultimo_uso and ultimo_uso.horometro_final:
                # El mínimo es el mayor entre el horómetro actual y el último horómetro final
                horometro_minimo = max(horometro_minimo, ultimo_uso.horometro_final)

            # Validar que el horómetro inicial sea mayor o igual al mínimo
            if self.horometro_inicial < horometro_minimo:
                if ultimo_uso and ultimo_uso.horometro_final:
                    raise ValidationError({
                        'horometro_inicial': f'El horómetro inicial no puede ser menor al último horómetro final registrado ({ultimo_uso.horometro_final} hrs)'
                    })
                else:
                    raise ValidationError({
                        'horometro_inicial': f'El horómetro inicial no puede ser menor al horómetro actual de la maquinaria ({self.maquinaria.horometro_actual} hrs)'
                    })


class HistorialTarifaMaquinaria(models.Model):
    """
    Historial de cambios en la tarifa de maquinaria.
    Se crea automáticamente cuando se modifica la tarifa_hora.
    """
    maquinaria = models.ForeignKey(
        Maquinaria,
        on_delete=models.CASCADE,
        related_name='historial_tarifas',
        verbose_name='Maquinaria'
    )
    tarifa_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Tarifa Anterior',
        null=True,
        blank=True
    )
    tarifa_nueva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Tarifa Nueva'
    )
    fecha_cambio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del Cambio'
    )
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cambios_tarifa_maquinaria',
        verbose_name='Usuario que Realizó el Cambio'
    )
    motivo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Motivo del Cambio',
        help_text='Ej: Ajuste por inflación, Cambio de mercado, etc.'
    )

    class Meta:
        verbose_name = 'Historial de Tarifa de Maquinaria'
        verbose_name_plural = 'Historial de Tarifas de Maquinaria'
        ordering = ['-fecha_cambio']

    def __str__(self):
        if self.tarifa_anterior:
            return f"{self.maquinaria.codigo}: L.{self.tarifa_anterior} → L.{self.tarifa_nueva} ({self.fecha_cambio.strftime('%d/%m/%Y')})"
        else:
            return f"{self.maquinaria.codigo}: Tarifa inicial L.{self.tarifa_nueva} ({self.fecha_cambio.strftime('%d/%m/%Y')})"


def pago_comprobante_upload_path(instance, filename):
    """
    Genera la ruta de subida de comprobantes de pago, separando por empresa.

    Estructura: pagos/<empresa_codigo>/<año>/<mes>/<filename>

    Ejemplo: pagos/empresa1/2025/01/comprobante_bac_123.jpg
    """
    empresa_codigo = instance.empresa.codigo
    fecha = instance.fecha_pago
    año = fecha.year
    mes = f"{fecha.month:02d}"

    # Limpiar el nombre del archivo
    nombre_base, extension = os.path.splitext(filename)
    nombre_limpio = slugify(nombre_base)
    filename_final = f"{nombre_limpio}{extension.lower()}"

    return f'pagos/{empresa_codigo}/{año}/{mes}/{filename_final}'


class PagoRecibido(models.Model):
    """
    Modelo para registrar pagos recibidos de empresas y gestionar la confirmación de suscripciones.
    Los administradores pueden revisar y confirmar pagos desde el Django Admin.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Confirmación'),
        ('confirmado', 'Confirmado'),
        ('rechazado', 'Rechazado'),
    ]

    METODO_PAGO_CHOICES = [
        ('transferencia_bac', 'Transferencia BAC'),
        ('transferencia_occidente', 'Transferencia Banco de Occidente'),
        ('deposito_bac', 'Depósito BAC'),
        ('deposito_occidente', 'Depósito Banco de Occidente'),
        ('otro', 'Otro'),
    ]

    PLAN_CHOICES = [
        # Planes Básicos
        ('mensual_nuevo_basico', 'Plan Mensual Básico - Nuevo Cliente (L. 10,000)'),
        ('anual_1_nuevo_basico', 'Plan Anual Básico 1 año - Nuevo Cliente (L. 28,700)'),
        ('anual_2_nuevo_basico', 'Plan Bianual Básico 2 años - Nuevo Cliente (L. 49,100)'),
        ('mensual_basico', 'Plan Mensual Básico - Renovación (L. 2,000)'),
        ('anual_1_basico', 'Plan Anual Básico 1 año - Renovación (L. 18,700)'),
        ('anual_2_basico', 'Plan Bianual Básico 2 años - Renovación (L. 39,100)'),

        # Planes Completos
        ('mensual_nuevo_completo', 'Plan Mensual Completo - Nuevo Cliente (L. 12,500)'),
        ('anual_1_nuevo_completo', 'Plan Anual Completo 1 año - Nuevo Cliente (L. 33,375)'),
        ('anual_2_nuevo_completo', 'Plan Bianual Completo 2 años - Nuevo Cliente (L. 58,875)'),
        ('mensual_completo', 'Plan Mensual Completo - Renovación (L. 2,500)'),
        ('anual_1_completo', 'Plan Anual Completo 1 año - Renovación (L. 23,375)'),
        ('anual_2_completo', 'Plan Bianual Completo 2 años - Renovación (L. 48,875)'),
    ]

    # Información del pago
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='pagos_recibidos',
        verbose_name='Empresa'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto Pagado'
    )
    fecha_pago = models.DateField(
        verbose_name='Fecha del Pago',
        help_text='Fecha en que se realizó la transferencia/depósito'
    )
    metodo_pago = models.CharField(
        max_length=30,
        choices=METODO_PAGO_CHOICES,
        default='transferencia_bac',
        verbose_name='Método de Pago'
    )
    plan_seleccionado = models.CharField(
        max_length=30,
        choices=PLAN_CHOICES,
        verbose_name='Plan Seleccionado',
        help_text='Plan que el cliente desea contratar'
    )

    # Comprobante
    comprobante = models.FileField(
        upload_to=pago_comprobante_upload_path,
        blank=True,
        null=True,
        validators=[
            validar_tamanio_archivo,
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])
        ],
        verbose_name='Comprobante de Pago',
        help_text='Adjuntar imagen o PDF del comprobante (máx. 10MB)'
    )
    referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Referencia/Número de Transacción',
        help_text='Número de referencia del banco'
    )

    # Estado y gestión
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    notas_cliente = models.TextField(
        blank=True,
        verbose_name='Notas del Cliente',
        help_text='Información adicional del cliente sobre el pago'
    )
    notas_admin = models.TextField(
        blank=True,
        verbose_name='Notas del Administrador',
        help_text='Notas internas sobre la verificación del pago'
    )

    # Fechas de gestión
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    fecha_confirmacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Confirmación',
        help_text='Fecha en que se confirmó el pago'
    )
    confirmado_por = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='pagos_confirmados',
        verbose_name='Confirmado Por'
    )

    class Meta:
        verbose_name = 'Pago Recibido'
        verbose_name_plural = 'Pagos Recibidos'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.empresa.nombre} - L. {self.monto:,.2f} - {self.get_estado_display()}"

    def confirmar_pago(self, usuario=None):
        """
        Confirma el pago y activa/renueva la suscripción de la empresa.
        Actualiza automáticamente todos los campos necesarios según el plan seleccionado.
        """
        from datetime import date, timedelta
        from .config_pagos import PLANES_PRECIOS

        if self.estado == 'confirmado':
            return False  # Ya está confirmado

        # Obtener información del plan
        plan_info = PLANES_PRECIOS.get(self.plan_seleccionado, {})

        # Determinar tipo de plan y si incluye maquinaria
        incluye_maquinaria = plan_info.get('incluye_maquinaria', True)

        # Determinar duración en días según el plan
        if 'anual_2' in self.plan_seleccionado or 'bianual' in self.plan_seleccionado:
            # Bianual: 23 meses = 690 días
            duracion_dias = 690
            tipo_suscripcion = 'anual'
        elif 'anual_1' in self.plan_seleccionado:
            # Anual: 11 meses = 330 días
            duracion_dias = 330
            tipo_suscripcion = 'anual'
        else:
            # Mensual: 30 días
            duracion_dias = 30
            tipo_suscripcion = 'mensual'

        # Actualizar empresa
        self.empresa.tipo_suscripcion = tipo_suscripcion
        self.empresa.estado_suscripcion = 'activa'
        self.empresa.plan_incluye_maquinaria = incluye_maquinaria

        # Si es nuevo cliente (plan con "nuevo" en el nombre), marcar cuota de instalación
        if 'nuevo' in self.plan_seleccionado:
            self.empresa.cuota_instalacion_pagada = True

        # Calcular fechas de suscripción
        # Si ya tiene suscripción activa, extender desde fecha de expiración
        # Si no, o si está vencida, empezar desde hoy
        if (self.empresa.fecha_expiracion_suscripcion and
            self.empresa.fecha_expiracion_suscripcion >= date.today()):
            # Extender desde la fecha de expiración actual
            self.empresa.fecha_inicio_suscripcion = self.empresa.fecha_expiracion_suscripcion
            self.empresa.fecha_expiracion_suscripcion = self.empresa.fecha_expiracion_suscripcion + timedelta(days=duracion_dias)
        else:
            # Empezar desde hoy
            self.empresa.fecha_inicio_suscripcion = date.today()
            self.empresa.fecha_expiracion_suscripcion = date.today() + timedelta(days=duracion_dias)

        self.empresa.save()

        # Actualizar estado del pago
        self.estado = 'confirmado'
        self.fecha_confirmacion = date.today()
        if usuario:
            self.confirmado_por = usuario
        self.save()

        return True

    def rechazar_pago(self, motivo='', usuario=None):
        """Rechaza el pago"""
        self.estado = 'rechazado'
        if motivo:
            self.notas_admin = f"{self.notas_admin}\n\nRECHAZADO: {motivo}".strip()
        if usuario:
            self.confirmado_por = usuario
        self.save()
