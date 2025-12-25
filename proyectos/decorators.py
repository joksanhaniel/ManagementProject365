from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def rol_requerido(*roles_permitidos):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos.

    Uso:
        @rol_requerido('administrador', 'gerente_proyecto')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
                return redirect('login')

            if request.user.rol not in roles_permitidos:
                messages.error(request, 'No tiene permisos para acceder a esta página.')
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def permiso_escritura_requerido(view_func):
    """
    Decorador que verifica si el usuario tiene permisos de escritura.
    Solo administradores y gerentes de proyecto pueden crear/editar/eliminar.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
            return redirect('login')

        if not request.user.tiene_permiso_escritura():
            messages.error(request, 'No tiene permisos para realizar esta acción.')
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return wrapped_view


def permiso_financiero_requerido(view_func):
    """
    Decorador que verifica si el usuario tiene acceso a información financiera.
    Administradores, gerentes y contadores tienen acceso.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
            return redirect('login')

        if not request.user.tiene_permiso_financiero():
            messages.error(request, 'No tiene permisos para acceder a información financiera.')
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return wrapped_view


def permiso_planillas_requerido(view_func):
    """
    Decorador que verifica si el usuario puede gestionar planillas.
    Administradores, gerentes y contadores tienen acceso.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
            return redirect('login')

        if not request.user.tiene_permiso_planillas():
            messages.error(request, 'No tiene permisos para gestionar planillas.')
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return wrapped_view


def permiso_empleados_requerido(view_func):
    """
    Decorador que verifica si el usuario puede gestionar empleados.
    Administradores, gerentes y supervisores tienen acceso.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debe iniciar sesión para acceder a esta página.')
            return redirect('login')

        if not request.user.tiene_permiso_empleados():
            messages.error(request, 'No tiene permisos para gestionar empleados.')
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return wrapped_view
