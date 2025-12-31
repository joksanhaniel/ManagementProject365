"""
Script para simular diferentes estados de suscripción y probar alertas.
Ejecutar con: python simular_alertas.py
"""
import os
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mpp365_system.settings')
django.setup()

from proyectos.models import Empresa

def mostrar_menu():
    print("\n" + "="*60)
    print("SIMULADOR DE ALERTAS DE SUSCRIPCIÓN")
    print("="*60)
    print("\nSelecciona el escenario a simular:\n")
    print("1. Alerta de 7 días (Warning - Amarillo)")
    print("2. Alerta de 3 días (Danger - Rojo urgente)")
    print("3. Alerta de 1 día (Danger - Muy urgente)")
    print("4. Suscripción vencida hace 5 días")
    print("5. Trial por vencer en 2 días")
    print("6. Resetear a estado normal (30 días)")
    print("7. Listar todas las empresas")
    print("0. Salir\n")

def listar_empresas():
    empresas = Empresa.objects.all()
    print("\n" + "="*60)
    print("EMPRESAS EN EL SISTEMA")
    print("="*60)
    for emp in empresas:
        print(f"\nID: {emp.id}")
        print(f"Código: {emp.codigo}")
        print(f"Nombre: {emp.nombre}")
        print(f"RTN: {emp.rtn}")
        print(f"Estado: {emp.estado_suscripcion}")
        print(f"Tipo: {emp.tipo_suscripcion}")
        if emp.fecha_expiracion_suscripcion:
            dias_restantes = (emp.fecha_expiracion_suscripcion - date.today()).days
            print(f"Vencimiento: {emp.fecha_expiracion_suscripcion} ({dias_restantes} días)")
        print("-" * 60)

def aplicar_escenario(empresa_id, opcion):
    try:
        empresa = Empresa.objects.get(id=empresa_id)
    except Empresa.DoesNotExist:
        print(f"\n❌ No existe empresa con ID {empresa_id}")
        return

    hoy = date.today()

    if opcion == '1':
        # Alerta de 7 días
        empresa.fecha_expiracion_suscripcion = hoy + timedelta(days=7)
        empresa.estado_suscripcion = 'activa'
        empresa.tipo_suscripcion = 'mensual'
        print(f"\n✅ Configurado: Vence en 7 días ({empresa.fecha_expiracion_suscripcion})")
        print("   → Alerta AMARILLA (warning)")

    elif opcion == '2':
        # Alerta de 3 días
        empresa.fecha_expiracion_suscripcion = hoy + timedelta(days=3)
        empresa.estado_suscripcion = 'activa'
        empresa.tipo_suscripcion = 'mensual'
        print(f"\n✅ Configurado: Vence en 3 días ({empresa.fecha_expiracion_suscripcion})")
        print("   → Alerta ROJA URGENTE (danger)")

    elif opcion == '3':
        # Alerta de 1 día
        empresa.fecha_expiracion_suscripcion = hoy + timedelta(days=1)
        empresa.estado_suscripcion = 'activa'
        empresa.tipo_suscripcion = 'mensual'
        print(f"\n✅ Configurado: Vence MAÑANA ({empresa.fecha_expiracion_suscripcion})")
        print("   → Alerta ROJA MUY URGENTE (danger)")

    elif opcion == '4':
        # Suscripción vencida
        empresa.fecha_expiracion_suscripcion = hoy - timedelta(days=5)
        empresa.estado_suscripcion = 'vencida'
        empresa.tipo_suscripcion = 'mensual'
        print(f"\n✅ Configurado: Vencida hace 5 días ({empresa.fecha_expiracion_suscripcion})")
        print("   → Alerta ROJA CRÍTICA (vencida)")

    elif opcion == '5':
        # Trial por vencer
        empresa.fecha_expiracion_suscripcion = hoy + timedelta(days=2)
        empresa.estado_suscripcion = 'trial'
        empresa.tipo_suscripcion = 'trial'
        print(f"\n✅ Configurado: Trial vence en 2 días ({empresa.fecha_expiracion_suscripcion})")
        print("   → Alerta ROJA (trial ending)")

    elif opcion == '6':
        # Estado normal
        empresa.fecha_expiracion_suscripcion = hoy + timedelta(days=30)
        empresa.estado_suscripcion = 'activa'
        empresa.tipo_suscripcion = 'mensual'
        print(f"\n✅ Configurado: Estado normal, vence en 30 días ({empresa.fecha_expiracion_suscripcion})")
        print("   → Sin alertas")

    empresa.save()
    print(f"\n💾 Cambios guardados para: {empresa.nombre}")
    print(f"\n🌐 Ingresa al dashboard: http://127.0.0.1:8000/{empresa.codigo}/")

def main():
    while True:
        mostrar_menu()
        opcion = input("Opción: ").strip()

        if opcion == '0':
            print("\n👋 Saliendo...\n")
            break

        elif opcion == '7':
            listar_empresas()
            input("\nPresiona Enter para continuar...")
            continue

        elif opcion in ['1', '2', '3', '4', '5', '6']:
            listar_empresas()
            try:
                empresa_id = int(input("\n📝 ID de la empresa a modificar: ").strip())
                aplicar_escenario(empresa_id, opcion)
                input("\nPresiona Enter para continuar...")
            except ValueError:
                print("\n❌ Debes ingresar un número válido")
                input("\nPresiona Enter para continuar...")
        else:
            print("\n❌ Opción no válida")
            input("\nPresiona Enter para continuar...")

if __name__ == '__main__':
    main()
