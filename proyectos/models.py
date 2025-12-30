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
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código',
                              help_text='Código único para identificar la empresa en URLs')
    nombre = models.CharField(max_length=200, verbose_name='Nombre Comercial')
    razon_social = models.CharField(max_length=200, verbose_name='Razón Social')
    rtn = models.CharField(max_length=14, unique=True, verbose_name='RTN')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    email = models.EmailField(blank=True, null=True, verbose_name='Correo Electrónico')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    logo = models.ImageField(upload_to='empresas/logos/', blank=True, null=True, verbose_name='Logo')
    activa = models.BooleanField(default=True, verbose_name='Empresa Activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Última Modificación')

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def get_url_prefix(self):
        """Retorna el prefijo de URL para esta empresa"""
        return self.codigo.lower()


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
        """Calcula el total de costos del proyecto (planilla + gastos)"""
        total_planilla = sum(p.monto_total for p in self.planillas.all())
        total_gastos = sum(g.monto for g in self.gastos.all())
        return total_planilla + total_gastos

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
    - Usuario: Solo lectura de proyectos y reportes

    Nota: El superusuario (is_superuser=True) tiene acceso completo al sistema incluyendo Django Admin
    """

    ROL_CHOICES = [
        ('gerente', 'Gerente'),
        ('supervisor', 'Supervisor'),
        ('contador', 'Contador'),
        ('auxiliar', 'Auxiliar'),
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
