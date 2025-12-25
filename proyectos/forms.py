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
        fields = '__all__'
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CLI001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Constructora ABC S.A.'}),
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
        fields = '__all__'
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
        fields = '__all__'
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
        super().__init__(*args, **kwargs)
        # Forzar formato de fecha para inputs type="date"
        self.fields['fecha_ingreso'].input_formats = ['%Y-%m-%d']


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = '__all__'
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
        super().__init__(*args, **kwargs)
        # Forzar formato de fecha para inputs type="date"
        self.fields['fecha_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_fin_estimada'].input_formats = ['%Y-%m-%d']
        if 'fecha_fin_real' in self.fields:
            self.fields['fecha_fin_real'].input_formats = ['%Y-%m-%d']


class AsignacionEmpleadoForm(forms.ModelForm):
    class Meta:
        model = AsignacionEmpleado
        fields = ['proyecto', 'empleado', 'activo']
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': 'checked'}),
        }

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
        super().__init__(*args, **kwargs)
        # Forzar formato de fecha para inputs type="date"
        self.fields['periodo_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['periodo_fin'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_pago'].input_formats = ['%Y-%m-%d']


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
        super().__init__(*args, **kwargs)
        # Si es una instancia existente, pre-llenar el salario devengado
        if self.instance and self.instance.pk:
            self.fields['salario_devengado'].initial = self.instance.salario_devengado


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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Forzar formato de fecha para inputs type="date"
        self.fields['fecha_gasto'].input_formats = ['%Y-%m-%d']
        if 'fecha_pago' in self.fields:
            self.fields['fecha_pago'].input_formats = ['%Y-%m-%d']
        # Filtrar solo proveedores activos
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True).order_by('nombre')


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


class UsuarioCreationForm(UserCreationForm):
    """Formulario para crear nuevos usuarios con roles"""

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'rol', 'is_active', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@constructora.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9999-9999'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].required = True


class UsuarioUpdateForm(forms.ModelForm):
    """Formulario para editar usuarios existentes"""

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'rol', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@constructora.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9999-9999'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True


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
        super().__init__(*args, **kwargs)
        self.fields['empleado'].queryset = Empleado.objects.filter(activo=True).order_by('nombres', 'apellidos')
        self.fields['planilla'].queryset = Planilla.objects.all().order_by('-fecha_pago')
