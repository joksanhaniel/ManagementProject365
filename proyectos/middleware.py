from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import Empresa


class EmpresaMiddleware:
    """
    Middleware que detecta la empresa actual desde la URL y la agrega al request.

    URLs esperadas: /empresax/proyectos/, /empresax/clientes/, etc.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
        else:
            request.empresa = None

        # Si el usuario está logueado y no es superusuario, validar que tenga acceso a la empresa
        if request.user.is_authenticated and not request.user.is_superuser:
            if request.empresa and request.user.empresa != request.empresa:
                # El usuario intenta acceder a una empresa que no es la suya
                if request.user.empresa:
                    # Redirigir a su empresa
                    return redirect(f'/{request.user.empresa.get_url_prefix()}{request.path[len(path_parts[0])+1:]}')
                else:
                    # Usuario sin empresa asignada - no debería pasar
                    pass

        response = self.get_response(request)
        return response


def empresa_context_processor(request):
    """
    Context processor que agrega la empresa actual a todos los templates.
    """
    empresa = getattr(request, 'empresa', None)
    return {
        'empresa_actual': empresa,
        'empresa_codigo': empresa.codigo if empresa else None,
        'es_superusuario': request.user.is_superuser if request.user.is_authenticated else False,
    }
