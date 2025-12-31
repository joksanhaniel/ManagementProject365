from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import Empresa
import logging

logger = logging.getLogger(__name__)


class EmpresaMiddleware:
    """
    Middleware que detecta la empresa actual desde la URL y la agrega al request.

    URLs esperadas: /empresax/proyectos/, /empresax/clientes/, etc.
    """

    # Rutas que no requieren validación de empresa
    EXCLUDED_PATHS = ['/login/', '/logout/', '/admin/', '/static/', '/media/', '/seleccionar-empresa/', '/api/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir rutas que no requieren validación de empresa
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            request.empresa = None
            return self.get_response(request)

        # Detectar empresa desde la URL
        path_parts = request.path.strip('/').split('/')

        # Si la ruta comienza con un código de empresa
        if path_parts and path_parts[0]:
            try:
                empresa = Empresa.objects.get(codigo__iexact=path_parts[0], activa=True)
                request.empresa = empresa
            except Empresa.DoesNotExist:
                # Si no existe la empresa, continuar sin empresa en el contexto
                request.empresa = None
            except Exception as e:
                logger.error(f"Error al obtener empresa: {e}")
                request.empresa = None
        else:
            request.empresa = None

        # Si el usuario está logueado y no es superusuario, validar que tenga acceso a la empresa
        if request.user.is_authenticated and not request.user.is_superuser:
            if request.empresa and request.user.empresa != request.empresa:
                # El usuario intenta acceder a una empresa que no es la suya
                if request.user.empresa:
                    # Redirigir a su empresa
                    new_path = request.path[len(path_parts[0])+1:]
                    redirect_url = f'/{request.user.empresa.get_url_prefix()}{new_path}'
                    logger.warning(f"Usuario {request.user.username} intentó acceder a empresa incorrecta. Redirigiendo.")
                    return redirect(redirect_url)
                else:
                    # Usuario sin empresa asignada - no debería pasar
                    logger.error(f"Usuario {request.user.username} sin empresa asignada intentó acceder al sistema")
                    pass

        response = self.get_response(request)
        return response


class SuscripcionMiddleware:
    """
    Middleware que valida el estado de la suscripción de la empresa.
    - Si la suscripción está vencida: bloquea acceso (solo lectura)
    - Si está en trial: permite acceso limitado
    - Si está activa: acceso completo
    """

    # Rutas que no requieren validación de suscripción
    EXCLUDED_PATHS = ['/', '/login/', '/logout/', '/admin/', '/static/', '/media/', '/registro/', '/terminos-condiciones/', '/api/']

    # Rutas permitidas incluso con suscripción vencida
    ALLOWED_WHEN_EXPIRED = ['/renovar-licencia/', '/perfil/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir rutas que no requieren validación
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return self.get_response(request)

        # Solo validar si hay una empresa en el request
        empresa = getattr(request, 'empresa', None)

        if empresa and request.user.is_authenticated and not request.user.is_superuser:
            # Actualizar estado de suscripción si está vencida
            if empresa.suscripcion_vencida() and empresa.estado_suscripcion != 'vencida':
                empresa.estado_suscripcion = 'vencida'
                empresa.save()

            # Si la suscripción está vencida, redirigir a página de renovación
            if empresa.estado_suscripcion == 'vencida':
                # Permitir acceso solo a ciertas rutas
                if not any(request.path.startswith(f'/{empresa.codigo}{path}') for path in self.ALLOWED_WHEN_EXPIRED):
                    logger.warning(f"Empresa {empresa.nombre} con suscripción vencida intentó acceder a {request.path}")
                    return redirect('renovar_licencia', empresa_codigo=empresa.codigo)

        response = self.get_response(request)
        return response


class MaquinariaAccessMiddleware:
    """
    Middleware que restringe el acceso al módulo de maquinaria según el plan de suscripción.
    - Plan Básico: No tiene acceso al módulo de maquinaria
    - Plan Completo: Acceso completo al módulo de maquinaria
    - Trial: Acceso completo para probar
    """

    # Rutas que no requieren validación
    EXCLUDED_PATHS = ['/', '/login/', '/logout/', '/admin/', '/static/', '/media/', '/registro/', '/terminos-condiciones/', '/api/']

    # Rutas del módulo de maquinaria que requieren validación
    MAQUINARIA_PATHS = ['/maquinarias/', '/maquinaria/', '/uso-maquinaria/', '/usos-maquinaria/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir rutas que no requieren validación
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return self.get_response(request)

        # Solo validar si hay una empresa en el request
        empresa = getattr(request, 'empresa', None)

        if empresa and request.user.is_authenticated and not request.user.is_superuser:
            # Verificar si la ruta es del módulo de maquinaria
            is_maquinaria_path = any(maq_path in request.path for maq_path in self.MAQUINARIA_PATHS)

            if is_maquinaria_path:
                # Si está en trial, permitir acceso completo
                if empresa.esta_en_trial():
                    return self.get_response(request)

                # Si no incluye maquinaria en el plan, bloquear acceso
                if not empresa.plan_incluye_maquinaria:
                    from django.contrib import messages
                    from django.shortcuts import render

                    logger.warning(f"Empresa {empresa.nombre} (Plan Básico) intentó acceder al módulo de maquinaria")

                    # Renderizar página de upgrade con mensaje
                    messages.warning(
                        request,
                        'Tu plan actual no incluye el módulo de gestión de maquinaria. '
                        'Actualiza a un Plan Completo para acceder a esta funcionalidad.'
                    )

                    # Crear contexto para la página de upgrade
                    context = {
                        'empresa_actual': empresa,
                        'modulo_requerido': 'Gestión de Maquinaria',
                        'plan_actual': 'Plan Básico',
                        'plan_requerido': 'Plan Completo',
                        'diferencia_precio': 500,
                    }

                    return render(request, 'proyectos/upgrade_required.html', context)

        response = self.get_response(request)
        return response


def empresa_context_processor(request):
    """
    Context processor que agrega la empresa actual y su estado de suscripción a todos los templates.
    """
    empresa = getattr(request, 'empresa', None)

    context = {
        'empresa_actual': empresa,
        'empresa_codigo': empresa.codigo if empresa else None,
        'es_superusuario': request.user.is_superuser if request.user.is_authenticated else False,
    }

    # Agregar información de suscripción
    if empresa:
        context['suscripcion_activa'] = empresa.suscripcion_activa()
        context['suscripcion_vencida'] = empresa.suscripcion_vencida()
        context['esta_en_trial'] = empresa.esta_en_trial()
        context['dias_restantes'] = empresa.dias_restantes()
        context['puede_crear_registros'] = empresa.puede_crear_registros()
        context['tipo_suscripcion'] = empresa.get_tipo_suscripcion_display()
        context['estado_suscripcion'] = empresa.get_estado_suscripcion_display()
        context['plan_incluye_maquinaria'] = empresa.plan_incluye_maquinaria
        context['es_plan_basico'] = not empresa.plan_incluye_maquinaria
        context['es_plan_completo'] = empresa.plan_incluye_maquinaria

    return context
