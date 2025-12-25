from rest_framework import serializers
from .models import (
    Cliente, Empleado, Proyecto, AsignacionEmpleado, Planilla,
    DetallePlanilla, Gasto, Pago
)


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class EmpleadoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model = Empleado
        fields = '__all__'


class AsignacionEmpleadoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    proyecto_nombre = serializers.CharField(source='proyecto.nombre', read_only=True)

    class Meta:
        model = AsignacionEmpleado
        fields = '__all__'


class DetallePlanillaSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = DetallePlanilla
        fields = '__all__'

    def get_total(self, obj):
        return float(obj.calcular_total())


class PlanillaSerializer(serializers.ModelSerializer):
    proyecto_nombre = serializers.CharField(source='proyecto.nombre', read_only=True)
    detalles = DetallePlanillaSerializer(many=True, read_only=True)
    monto_total = serializers.SerializerMethodField()

    class Meta:
        model = Planilla
        fields = '__all__'

    def get_monto_total(self, obj):
        return float(obj.monto_total)


class GastoSerializer(serializers.ModelSerializer):
    proyecto_nombre = serializers.CharField(source='proyecto.nombre', read_only=True)

    class Meta:
        model = Gasto
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    proyecto_nombre = serializers.CharField(source='proyecto.nombre', read_only=True)

    class Meta:
        model = Pago
        fields = '__all__'


class ProyectoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    costos_totales = serializers.SerializerMethodField()
    utilidad_bruta = serializers.SerializerMethodField()
    margen_utilidad = serializers.SerializerMethodField()
    asignaciones = AsignacionEmpleadoSerializer(many=True, read_only=True)
    planillas = PlanillaSerializer(many=True, read_only=True)
    gastos = GastoSerializer(many=True, read_only=True)
    pagos = PagoSerializer(many=True, read_only=True)

    class Meta:
        model = Proyecto
        fields = '__all__'

    def get_costos_totales(self, obj):
        return float(obj.calcular_costos_totales())

    def get_utilidad_bruta(self, obj):
        return float(obj.calcular_utilidad_bruta())

    def get_margen_utilidad(self, obj):
        return float(obj.calcular_margen_utilidad())


class ProyectoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de proyectos"""
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    costos_totales = serializers.SerializerMethodField()
    utilidad_bruta = serializers.SerializerMethodField()
    margen_utilidad = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = ['id', 'codigo', 'nombre', 'cliente', 'cliente_nombre', 'monto_contrato',
                  'estado', 'porcentaje_avance', 'fecha_inicio', 'fecha_fin_estimada',
                  'costos_totales', 'utilidad_bruta', 'margen_utilidad']

    def get_costos_totales(self, obj):
        return float(obj.calcular_costos_totales())

    def get_utilidad_bruta(self, obj):
        return float(obj.calcular_utilidad_bruta())

    def get_margen_utilidad(self, obj):
        return float(obj.calcular_margen_utilidad())
