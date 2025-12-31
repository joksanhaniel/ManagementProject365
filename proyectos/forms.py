from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    Cliente, Proveedor, Empleado, Proyecto, AsignacionEmpleado, Planilla,
    DetallePlanilla, Gasto, Pago, Usuario, Deduccion, Bonificacion, HoraExtra
)


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = ['empresa']  # Empresa se asigna automáticamente en la vista
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CLI001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Empresa ABC S.A.'}),
            'rtn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01019012345678'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2234-5678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@empresa.hn'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan Pérez'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        exclude = ['empresa']  # Empresa se asigna automáticamente en la vista
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PROV001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ferretería Central S.A.'}),
            'rtn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01019012345678'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2234-5678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ventas@proveedor.hn'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'María López'}),
            'tipo_proveedor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Materiales'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        exclude = ['empresa']  # Empresa se asigna automáticamente en la vista
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'EMP001'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0801-1990-12345'}),
            'rtn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08011990123456'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '7890-1234'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Maestro de Obra'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'salario_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '800.00'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        # Forzar formato de fecha para inputs type="date"
        self.fields['fecha_ingreso'].input_formats = ['%Y-%m-%d']


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        exclude = ['empresa']  # Empresa se asigna automáticamente en la vista
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PROY001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Casa Residencial'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'monto_contrato': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '50000.00'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'fecha_fin_estimada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'fecha_fin_real': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'porcentaje_avance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '0'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        # Forzar formato de fecha para inputs type="date"
        self.fields['fecha_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_fin_estimada'].input_formats = ['%Y-%m-%d']
        if 'fecha_fin_real' in self.fields:
            self.fields['fecha_fin_real'].input_formats = ['%Y-%m-%d']

        # Filtrar clientes por empresa
        if empresa:
            from .models import Cliente
            self.fields['cliente'].queryset = Cliente.objects.filter(empresa=empresa).order_by('nombre')
        else:
            from .models import Cliente
            self.fields['cliente'].queryset = Cliente.objects.filter(activo=True).order_by('nombre')


class AsignacionEmpleadoForm(forms.ModelForm):
    class Meta:
        model = AsignacionEmpleado
        fields = ['proyecto', 'empleado', 'activo']
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': 'checked'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        # Filtrar proyectos y empleados por empresa
        if empresa:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(empresa=empresa).order_by('nombre')
            self.fields['empleado'].queryset = Empleado.objects.filter(empresa=empresa, activo=True).order_by('apellidos', 'nombres')
        else:
            self.fields['empleado'].queryset = Empleado.objects.filter(activo=True).order_by('apellidos', 'nombres')

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Auto-llenar fecha_asignacion con la fecha actual si es nuevo
        if not instance.pk:
            from django.utils import timezone
            instance.fecha_asignacion = timezone.now().date()
        if commit:
            instance.save()
        return instance


class PlanillaForm(forms.ModelForm):
    class Meta:
        model = Planilla
        fields = '__all__'
        widgets = {
            'proyecto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'periodo_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'periodo_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'tipo_planilla': forms.Select(attrs={'class': 'form-select'}),
            'fecha_pago': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pagada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        # Forzar formato de fecha para inputs type="date"
        self.fields['periodo_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['periodo_fin'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_pago'].input_formats = ['%Y-%m-%d']

        # Filtrar proyectos por empresa
        if empresa:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(empresa=empresa).order_by('nombre')


class DetallePlanillaForm(forms.ModelForm):
    # Campo extra para mostrar el salario devengado (solo lectura)
    salario_devengado = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control salario-devengado',
            'step': '0.01',
            'placeholder': '0.00',
            'readonly': 'readonly'
        })
    )

    class Meta:
        model = DetallePlanilla
        fields = ['empleado']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select empleado-select'}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        # Si es una instancia existente, pre-llenar el salario devengado
        if self.instance and self.instance.pk:
            self.fields['salario_devengado'].initial = self.instance.salario_devengado

        # Filtrar empleados por empresa
        if empresa:
            self.fields['empleado'].queryset = Empleado.objects.filter(empresa=empresa, activo=True).order_by('apellidos', 'nombres')
        else:
            self.fields['empleado'].queryset = Empleado.objects.filter(activo=True).order_by('apellidos', 'nombres')


# Formset para gestionar múltiples detalles de planilla
DetallePlanillaFormSet = inlineformset_factory(
    Planilla,
    DetallePlanilla,
    form=DetallePlanillaForm,
    extra=0,  # No mostrar formularios vacíos, se agregan con JavaScript
    can_delete=True,  # Permitir eliminar líneas
    min_num=0,  # Permitir planilla sin empleados inicialmente
    validate_min=False
)


# Formset para gestionar deducciones de una planilla
DeduccionFormSet = inlineformset_factory(
    Planilla,
    Deduccion,
    fields=['empleado', 'descripcion', 'monto'],
    extra=0,
    can_delete=True,
    widgets={
        'empleado': forms.Select(attrs={'class': 'form-select'}),
        'descripcion': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'IHSS, ISR, Préstamo, Anticipo...'
        }),
        'monto': forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
    }
)


# Formset para gestionar bonificaciones de una planilla
BonificacionFormSet = inlineformset_factory(
    Planilla,
    Bonificacion,
    fields=['empleado', 'descripcion', 'monto'],
    extra=0,
    can_delete=True,
    widgets={
        'empleado': forms.Select(attrs={'class': 'form-select'}),
        'descripcion': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bono por rendimiento, Incentivo...'
        }),
        'monto': forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
    }
)


# Formset para gestionar horas extra de una planilla
HoraExtraFormSet = inlineformset_factory(
    Planilla,
    HoraExtra,
    fields=['empleado', 'descripcion', 'cantidad_horas', 'monto'],
    extra=0,
    can_delete=True,
    widgets={
        'empleado': forms.Select(attrs={'class': 'form-select'}),
        'descripcion': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Horas extra nocturnas, Domingo...'
        }),
        'cantidad_horas': forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
        'monto': forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
    }
)


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = '__all__'
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'tipo_gasto': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Compra de cemento y arena'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '1500.00'}),
            'fecha_gasto': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'F-12345'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_pago': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'archivo_adjunto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.xlsx,.xls,.doc,.docx'
            }),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        # Forzar formato de fecha para inputs type="date"
        self.fields['fecha_gasto'].input_formats = ['%Y-%m-%d']
        if 'fecha_pago' in self.fields:
            self.fields['fecha_pago'].input_formats = ['%Y-%m-%d']
            self.fields['fecha_pago'].required = False  # Campo opcional
        # Hacer proveedor opcional
        self.fields['proveedor'].required = False

        # Filtrar por empresa si está disponible
        if empresa:
            from .models import Proyecto, Proveedor
            self.fields['proyecto'].queryset = Proyecto.objects.filter(empresa=empresa).order_by('nombre')
            self.fields['proveedor'].queryset = Proveedor.objects.filter(empresa=empresa, activo=True).order_by('nombre')
        else:
            from .models import Proveedor
            self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True).order_by('nombre')

    def clean_fecha_pago(self):
        """Limpiar campo de fecha de pago opcional"""
        fecha_pago = self.cleaned_data.get('fecha_pago')
        # Si está vacío o es None, retornar None
        if not fecha_pago or fecha_pago == '':
            return None
        return fecha_pago

    def clean_archivo_adjunto(self):
        """Validar tamaño del archivo (máximo 10MB)"""
        archivo = self.cleaned_data.get('archivo_adjunto')
        if archivo:
            # Límite de 10MB
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no debe superar los 10MB.')
        return archivo


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = '__all__'
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '10000.00'}),
            'fecha_pago': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'forma_pago': forms.Select(attrs={'class': 'form-select'}),
            'numero_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'REF-12345'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        # Filtrar proyectos por empresa
        if empresa:
            self.fields['proyecto'].queryset = Proyecto.objects.filter(empresa=empresa).order_by('nombre')


class UsuarioCreationForm(UserCreationForm):
    """Formulario para crear nuevos usuarios con roles"""

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'rol', 'empresa', 'is_active', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@empresa.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9999-9999'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].required = True
        # Solo requerir empresa para usuarios no-superusuarios
        self.fields['empresa'].required = False
        self.fields['empresa'].help_text = 'Dejar en blanco para superusuarios'


class UsuarioUpdateForm(forms.ModelForm):
    """Formulario para editar usuarios existentes"""

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'rol', 'empresa', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@empresa.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9999-9999'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        # Solo requerir empresa para usuarios no-superusuarios
        self.fields['empresa'].required = False
        self.fields['empresa'].help_text = 'Dejar en blanco para superusuarios'


# ====== FORMULARIOS DE PRÉSTAMOS, ANTICIPOS Y SALARIOS ======

class DeduccionForm(forms.ModelForm):
    """Formulario para crear deducciones en planillas"""

    class Meta:
        model = Deduccion
        fields = ['planilla', 'empleado', 'descripcion', 'monto']
        widgets = {
            'planilla': forms.Select(attrs={'class': 'form-select'}),
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: IHSS, ISR, Préstamo, Anticipo...'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        # Filtrar empleados y planillas por empresa
        if empresa:
            self.fields['empleado'].queryset = Empleado.objects.filter(empresa=empresa, activo=True).order_by('apellidos', 'nombres')
            self.fields['planilla'].queryset = Planilla.objects.filter(proyecto__empresa=empresa).order_by('-fecha_pago')
        else:
            self.fields['empleado'].queryset = Empleado.objects.filter(activo=True).order_by('apellidos', 'nombres')
            self.fields['planilla'].queryset = Planilla.objects.all().order_by('-fecha_pago')


# ====== FORMULARIOS DE MAQUINARIA ======

class MaquinariaForm(forms.ModelForm):
    """Formulario para crear y editar maquinarias"""

    class Meta:
        from .models import Maquinaria
        model = Maquinaria
        exclude = ['empresa']  # Empresa se asigna automáticamente en la vista
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'MAQ001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Retroexcavadora CAT 320'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Caterpillar'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '320D'
            }),
            'placa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PBC-1234'
            }),
            'horometro_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'tarifa_hora': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '500.00'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class UsoMaquinariaForm(forms.ModelForm):
    """Formulario para registrar uso de maquinaria en proyectos"""

    class Meta:
        from .models import UsoMaquinaria
        model = UsoMaquinaria
        fields = ['proyecto', 'maquinaria', 'fecha_inicio', 'fecha_fin', 'horometro_inicial',
                  'horometro_final', 'tarifa_aplicada', 'operador', 'descripcion_trabajo', 'observaciones']
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'maquinaria': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'horometro_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1000.00',
                'readonly': 'readonly'
            }),
            'horometro_final': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1050.00'
            }),
            'tarifa_aplicada': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '500.00',
                'readonly': 'readonly'
            }),
            'operador': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion_trabajo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Excavación de zanja para cimientos'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        # Forzar formato de fecha para inputs type="date"
        self.fields['fecha_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_fin'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_fin'].required = False
        self.fields['horometro_final'].required = False
        self.fields['operador'].required = False

        # Filtrar proyectos, maquinarias y operadores por empresa
        if empresa:
            from .models import Proyecto, Maquinaria, Usuario
            self.fields['proyecto'].queryset = Proyecto.objects.filter(empresa=empresa).order_by('nombre')

            # Filtrar maquinarias: solo mostrar disponibles en creación, todas en edición
            if self.instance and self.instance.pk:
                # En edición, mostrar todas (para que se pueda ver la seleccionada)
                self.fields['maquinaria'].queryset = Maquinaria.objects.filter(empresa=empresa, activo=True).order_by('codigo')
            else:
                # En creación, solo mostrar disponibles
                self.fields['maquinaria'].queryset = Maquinaria.objects.filter(
                    empresa=empresa,
                    activo=True,
                    estado='disponible'
                ).order_by('codigo')

            # Filtrar operadores: solo usuarios con rol 'operador'
            self.fields['operador'].queryset = Usuario.objects.filter(
                empresa=empresa,
                rol='operador',
                is_active=True
            ).order_by('username')

    def clean(self):
        cleaned_data = super().clean()
        horometro_inicial = cleaned_data.get('horometro_inicial')
        horometro_final = cleaned_data.get('horometro_final')

        # Validar que horómetro final sea mayor que inicial
        if horometro_final and horometro_inicial:
            if horometro_final <= horometro_inicial:
                raise forms.ValidationError({
                    'horometro_final': 'El horómetro final debe ser mayor al inicial'
                })

        return cleaned_data


# ====== FORMULARIO DE EMPRESAS ======

class EmpresaForm(forms.ModelForm):
    """Formulario para crear y editar empresas"""

    class Meta:
        from .models import Empresa
        model = Empresa
        fields = '__all__'
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'EMPRESA1',
                'pattern': '[A-Z0-9]+',
                'title': 'Solo letras mayúsculas y números, sin espacios'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Empresa ABC'
            }),
            'razon_social': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Empresa ABC S.A. de C.V.'
            }),
            'rtn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '08011234567890'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2234-5678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'info@empresa.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa de la empresa'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_codigo(self):
        """Validar que el código esté en mayúsculas y sin espacios"""
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            codigo = codigo.upper().replace(' ', '')
        return codigo
