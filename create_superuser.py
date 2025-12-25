"""
Script para crear el superusuario inicial con rol de administrador
IMPORTANTE: Solo para desarrollo. En producción usar credenciales seguras.
"""
import os
import django
import getpass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'constructora_system.settings')
django.setup()

from proyectos.models import Usuario

def create_superuser():
    print("=== Creacion de Superusuario Administrador ===\n")

    # Verificar si ya existe un superusuario
    if Usuario.objects.filter(is_superuser=True).exists():
        print("ADVERTENCIA: Ya existe un superusuario en la base de datos")
        usuario = Usuario.objects.filter(is_superuser=True).first()
        print(f"  Usuario: {usuario.username}")
        print(f"  Email: {usuario.email}")
        print(f"  Rol: {usuario.get_rol_display()}")

        overwrite = input("\nDesea crear un nuevo superusuario? (si/no): ")
        if overwrite.lower() not in ['si', 's', 'yes', 'y']:
            print("Operacion cancelada.")
            return

    # Solicitar datos del superusuario
    print("\nIngrese los datos del superusuario:")
    username = input("Nombre de usuario: ").strip()
    if not username:
        username = 'admin'

    email = input("Email: ").strip()
    if not email:
        email = 'admin@constructora.com'

    first_name = input("Nombres: ").strip() or 'Administrador'
    last_name = input("Apellidos: ").strip() or 'Sistema'

    # Solicitar contraseña segura
    while True:
        password = getpass.getpass("Contrasena (minimo 8 caracteres): ")
        if len(password) < 8:
            print("ERROR: La contrasena debe tener al menos 8 caracteres")
            continue

        password_confirm = getpass.getpass("Confirmar contrasena: ")
        if password != password_confirm:
            print("ERROR: Las contrasenas no coinciden")
            continue

        break

    # Crear el superusuario
    try:
        usuario = Usuario.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            rol='administrador',
            telefono='',
        )

        print("\n" + "=" * 50)
        print("Superusuario creado exitosamente!")
        print("=" * 50)
        print(f"Usuario: {usuario.username}")
        print(f"Email: {usuario.email}")
        print(f"Rol: {usuario.get_rol_display()}")
        print("=" * 50)
        print("\nAhora puedes acceder a:")
        print("  - Sistema: http://localhost:8000/")
        print("  - Admin: http://localhost:8000/admin/")
        print("\nRECUERDA: Usa una contrasena fuerte en produccion")

    except Exception as e:
        print(f"\nError al crear superusuario: {e}")

if __name__ == '__main__':
    create_superuser()
