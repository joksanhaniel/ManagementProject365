from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Empleado, HistorialSalario


@receiver(pre_save, sender=Empleado)
def crear_historial_salario(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de guardar un empleado.
    Si el salario_base ha cambiado, crea un registro en HistorialSalario.
    """
    # Solo procesar si el empleado ya existe (no es nuevo)
    if instance.pk:
        try:
            # Obtener el empleado original de la base de datos
            empleado_anterior = Empleado.objects.get(pk=instance.pk)

            # Verificar si el salario ha cambiado
            if empleado_anterior.salario_base != instance.salario_base:
                # Crear registro en el historial
                # Nota: No podemos obtener el usuario aquí directamente,
                # por lo que se debe establecer en el admin o view si es necesario
                HistorialSalario.objects.create(
                    empleado=instance,
                    salario_anterior=empleado_anterior.salario_base,
                    salario_nuevo=instance.salario_base,
                    motivo='Cambio de salario base'
                )
        except Empleado.DoesNotExist:
            # El empleado no existía antes, es nuevo
            pass
    else:
        # Es un nuevo empleado, crear el primer registro de historial
        # Esto se hará en post_save para asegurarnos de que tenga pk
        pass


@receiver(pre_save, sender=Empleado)
def crear_historial_salario_inicial(sender, instance, created=False, **kwargs):
    """
    Signal para crear el historial cuando se crea un nuevo empleado.
    """
    # Solo para nuevos empleados (sin pk aún)
    if not instance.pk and instance.salario_base:
        # Marcar para crear historial después del save
        instance._crear_historial_inicial = True


# Alternativa: usar post_save para empleados nuevos
from django.db.models.signals import post_save

@receiver(post_save, sender=Empleado)
def crear_historial_inicial_empleado(sender, instance, created, **kwargs):
    """
    Crea el primer registro de historial cuando se crea un empleado nuevo.
    """
    if created and instance.salario_base:
        HistorialSalario.objects.create(
            empleado=instance,
            salario_anterior=None,
            salario_nuevo=instance.salario_base,
            motivo='Salario inicial al crear empleado'
        )
