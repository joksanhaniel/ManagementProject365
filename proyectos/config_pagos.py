# Configuración de información de pagos para MPP365
# Este archivo contiene la información de contacto y cuentas bancarias para recibir pagos

CONTACTO_PAGOS = {
    'nombre': 'JOKSAN HANIEL PEREZ RAMOS',
    'email': 'joksanhaniel@gmail.com',
    'whatsapp': '+50495206618',
    'whatsapp_link': 'https://wa.me/50495206618',
}

CUENTAS_BANCARIAS = [
    {
        'banco': 'BAC',
        'numero_cuenta': '748235275',
        'titular': 'JOKSAN HANIEL PEREZ RAMOS',
        'tipo': 'Ahorro',
    },
    {
        'banco': 'Banco de Occidente',
        'numero_cuenta': '21-126-003139-7',
        'titular': 'JOKSAN HANIEL PEREZ RAMOS',
        'tipo': 'Ahorro',
    },
]

PLANES_PRECIOS = {
    # ==================== PLANES BÁSICOS (SIN MÓDULO DE MAQUINARIA) ====================

    # PRECIOS PARA CLIENTES NUEVOS - PLAN BÁSICO (incluyen cuota de activación)
    'mensual_nuevo_basico': {
        'nombre': 'Plan Mensual Básico',
        'precio': 10000,  # L. 10,000 activación (reducido de 20,000)
        'tipo_plan': 'basico',
        'incluye_maquinaria': False,
        'descripcion': 'Activación + Mes 1 Gratis (luego L. 2,000/mes)',
        'incluye': [
            'Activación y configuración de cuenta',
            'Capacitación básica para administradores',
            'Primer mes GRATIS (valor L. 2,000)',
            'A partir del mes 2: L. 2,000/mes',
            'Gestión de proyectos, empleados, planillas y gastos',
            'Flexibilidad mes a mes',
        ]
    },
    'anual_1_nuevo_basico': {
        'nombre': 'Plan Anual Básico (1 año)',
        'precio': 28700,  # 10,000 + 18,700
        'precio_mensual': 1700,  # 15% descuento (reducido de 1,800)
        'tipo_plan': 'basico',
        'incluye_maquinaria': False,
        'meses_totales': 12,  # 1 mes gratis + 11 meses prepagados
        'precio_original': 32000,  # 10,000 + (2,000 x 11)
        'ahorro': 3300,  # Ahorro aumentado
        'descripcion': 'Activación + Mes 1 Gratis + 11 Meses Prepagados',
        'incluye': [
            'Activación y configuración de cuenta',
            'Primer mes GRATIS (valor L. 2,000)',
            '11 meses prepagados a L. 1,700/mes',
            'Total: 12 meses de acceso',
            'Gestión de proyectos, empleados, planillas y gastos',
            'Ahorro de L. 3,300 vs plan mensual',
        ]
    },
    'anual_2_nuevo_basico': {
        'nombre': 'Plan Bianual Básico (2 años)',
        'precio': 49100,  # 10,000 + 39,100
        'precio_mensual': 1700,  # 15% descuento
        'tipo_plan': 'basico',
        'incluye_maquinaria': False,
        'meses_totales': 24,  # 1 mes gratis + 23 meses prepagados
        'precio_original': 56000,  # 10,000 + (2,000 x 23)
        'ahorro': 6900,  # Ahorro aumentado
        'descripcion': 'Activación + Mes 1 Gratis + 23 Meses Prepagados',
        'incluye': [
            'Activación y configuración de cuenta',
            'Primer mes GRATIS (valor L. 2,000)',
            '23 meses prepagados a L. 1,700/mes',
            'Total: 24 meses (2 años) de acceso',
            'Gestión de proyectos, empleados, planillas y gastos',
            'Ahorro de L. 6,900 vs plan mensual',
            'Máximo ahorro disponible',
        ]
    },

    # PRECIOS PARA RENOVACIONES - PLAN BÁSICO (sin cuota de instalación)
    'mensual_basico': {
        'nombre': 'Plan Mensual Básico',
        'precio': 2000,
        'tipo_plan': 'basico',
        'incluye_maquinaria': False,
        'descripcion': 'Suscripción mensual - Pago mes a mes',
        'incluye': [
            'Gestión de proyectos, empleados, planillas y gastos',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte por WhatsApp',
            'Actualizaciones automáticas',
        ]
    },
    'anual_1_basico': {
        'nombre': 'Plan Anual Básico (1 año)',
        'precio': 18700,  # Reducido de 19,800
        'precio_mensual': 1700,  # 15% descuento (reducido de 1,800)
        'tipo_plan': 'basico',
        'incluye_maquinaria': False,
        'meses': 11,
        'precio_original': 22000,
        'ahorro': 3300,  # Ahorro aumentado
        'descripcion': 'Suscripción anual: L. 1,700/mes x 11 meses',
        'incluye': [
            'Gestión de proyectos, empleados, planillas y gastos',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte prioritario por WhatsApp',
            'Actualizaciones automáticas',
            'Ahorro de L. 3,300 vs plan mensual',
        ]
    },
    'anual_2_basico': {
        'nombre': 'Plan Bianual Básico (2 años)',
        'precio': 39100,  # Reducido de 41,400
        'precio_mensual': 1700,  # 15% descuento
        'tipo_plan': 'basico',
        'incluye_maquinaria': False,
        'meses': 23,
        'precio_original': 46000,
        'ahorro': 6900,  # Ahorro aumentado
        'descripcion': 'Suscripción bianual: L. 1,700/mes x 23 meses',
        'incluye': [
            'Gestión de proyectos, empleados, planillas y gastos',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte prioritario por WhatsApp',
            'Actualizaciones automáticas',
            'Ahorro de L. 6,900 vs plan mensual',
            'Máximo ahorro disponible',
        ]
    },

    # ==================== PLANES COMPLETOS (CON MÓDULO DE MAQUINARIA) ====================

    # PRECIOS PARA CLIENTES NUEVOS - PLAN COMPLETO (incluyen cuota de activación)
    'mensual_nuevo_completo': {
        'nombre': 'Plan Mensual Completo',
        'precio': 12500,  # L. 10,000 activación + 2,500 mes 1 (reducido de 25,500)
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'descripcion': 'Activación + Mes 1 Gratis (luego L. 2,500/mes)',
        'incluye': [
            'Activación y configuración de cuenta',
            'Capacitación básica para administradores',
            'Primer mes GRATIS (valor L. 2,500)',
            'A partir del mes 2: L. 2,500/mes',
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Flexibilidad mes a mes',
        ]
    },
    'anual_1_nuevo_completo': {
        'nombre': 'Plan Anual Completo (1 año)',
        'precio': 33375,  # 10,000 + 23,375 (reducido de 45,300)
        'precio_mensual': 2125,  # 15% descuento (reducido de 2,300)
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'meses_totales': 12,  # 1 mes gratis + 11 meses prepagados
        'precio_original': 37500,  # 10,000 + (2,500 x 11)
        'ahorro': 4125,  # Ahorro aumentado
        'descripcion': 'Activación + Mes 1 Gratis + 11 Meses Prepagados',
        'incluye': [
            'Activación y configuración de cuenta',
            'Primer mes GRATIS (valor L. 2,500)',
            '11 meses prepagados a L. 2,125/mes',
            'Total: 12 meses de acceso',
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Ahorro de L. 4,125 vs plan mensual',
        ]
    },
    'anual_2_nuevo_completo': {
        'nombre': 'Plan Bianual Completo (2 años)',
        'precio': 58875,  # 10,000 + 48,875 (reducido de 72,900)
        'precio_mensual': 2125,  # 15% descuento
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'meses_totales': 24,  # 1 mes gratis + 23 meses prepagados
        'precio_original': 67500,  # 10,000 + (2,500 x 23)
        'ahorro': 8625,  # Ahorro aumentado
        'descripcion': 'Activación + Mes 1 Gratis + 23 Meses Prepagados',
        'incluye': [
            'Activación y configuración de cuenta',
            'Primer mes GRATIS (valor L. 2,500)',
            '23 meses prepagados a L. 2,125/mes',
            'Total: 24 meses (2 años) de acceso',
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Ahorro de L. 8,625 vs plan mensual',
            'Máximo ahorro disponible',
        ]
    },

    # PRECIOS PARA RENOVACIONES - PLAN COMPLETO (sin cuota de instalación)
    'mensual_completo': {
        'nombre': 'Plan Mensual Completo',
        'precio': 2500,
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'descripcion': 'Suscripción mensual - Pago mes a mes',
        'incluye': [
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte por WhatsApp',
            'Actualizaciones automáticas',
        ]
    },
    'anual_1_completo': {
        'nombre': 'Plan Anual Completo (1 año)',
        'precio': 23375,  # Reducido de 25,300
        'precio_mensual': 2125,  # 15% descuento (reducido de 2,300)
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'meses': 11,
        'precio_original': 27500,
        'ahorro': 4125,  # Ahorro aumentado
        'descripcion': 'Suscripción anual: L. 2,125/mes x 11 meses',
        'incluye': [
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte prioritario por WhatsApp',
            'Actualizaciones automáticas',
            'Ahorro de L. 4,125 vs plan mensual',
        ]
    },
    'anual_2_completo': {
        'nombre': 'Plan Bianual Completo (2 años)',
        'precio': 48875,  # Reducido de 52,900
        'precio_mensual': 2125,  # 15% descuento
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'meses': 23,
        'precio_original': 57500,
        'ahorro': 8625,  # Ahorro aumentado
        'descripcion': 'Suscripción bianual: L. 2,125/mes x 23 meses',
        'incluye': [
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte prioritario por WhatsApp',
            'Actualizaciones automáticas',
            'Ahorro de L. 8,625 vs plan mensual',
            'Máximo ahorro disponible',
        ]
    },

    # ==================== PLANES LEGACY (MANTENER COMPATIBILIDAD) ====================
    # Estos se mantienen por compatibilidad con código existente
    # Automáticamente redirigen a los planes completos
    'mensual_nuevo': {
        'nombre': 'Plan Mensual - Nuevos Clientes',
        'precio': 12500,  # Actualizado con nuevos precios
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'descripcion': 'Activación + Mes 1 Gratis (luego L. 2,500/mes)',
        'incluye': [
            'Activación y configuración de cuenta',
            'Capacitación básica para administradores',
            'Primer mes GRATIS (valor L. 2,500)',
            'A partir del mes 2: L. 2,500/mes',
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Flexibilidad mes a mes',
        ]
    },
    'anual_1_nuevo': {
        'nombre': 'Plan Anual (1 año) - Nuevos Clientes',
        'precio': 33375,  # Actualizado con nuevos precios
        'precio_mensual': 2125,
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'meses_totales': 12,
        'precio_original': 37500,
        'ahorro': 4125,
        'descripcion': 'Activación + Mes 1 Gratis + 11 Meses Prepagados',
        'incluye': [
            'Activación y configuración de cuenta',
            'Primer mes GRATIS (valor L. 2,500)',
            '11 meses prepagados a L. 2,125/mes',
            'Total: 12 meses de acceso',
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Ahorro de L. 4,125 vs plan mensual',
        ]
    },
    'anual_2_nuevo': {
        'nombre': 'Plan Bianual (2 años) - Nuevos Clientes',
        'precio': 58875,  # Actualizado con nuevos precios
        'precio_mensual': 2125,
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'meses_totales': 24,
        'precio_original': 67500,
        'ahorro': 8625,
        'descripcion': 'Activación + Mes 1 Gratis + 23 Meses Prepagados',
        'incluye': [
            'Activación y configuración de cuenta',
            'Primer mes GRATIS (valor L. 2,500)',
            '23 meses prepagados a L. 2,125/mes',
            'Total: 24 meses (2 años) de acceso',
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Ahorro de L. 8,625 vs plan mensual',
            'Máximo ahorro disponible',
        ]
    },
    'mensual': {
        'nombre': 'Plan Mensual',
        'precio': 2500,
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'descripcion': 'Suscripción mensual - Pago mes a mes',
        'incluye': [
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte por WhatsApp',
            'Actualizaciones automáticas',
        ]
    },
    'anual_1': {
        'nombre': 'Plan Anual (1 año)',
        'precio': 23375,  # Actualizado con nuevos precios
        'precio_mensual': 2125,
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'meses': 11,
        'precio_original': 27500,
        'ahorro': 4125,
        'descripcion': 'Suscripción anual: L. 2,125/mes x 11 meses',
        'incluye': [
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte prioritario por WhatsApp',
            'Actualizaciones automáticas',
            'Ahorro de L. 4,125 vs plan mensual',
        ]
    },
    'anual_2': {
        'nombre': 'Plan Bianual (2 años)',
        'precio': 48875,  # Actualizado con nuevos precios
        'precio_mensual': 2125,
        'tipo_plan': 'completo',
        'incluye_maquinaria': True,
        'meses': 23,
        'precio_original': 57500,
        'ahorro': 8625,
        'descripcion': 'Suscripción bianual: L. 2,125/mes x 23 meses',
        'incluye': [
            'Gestión completa: proyectos, empleados, planillas, gastos y maquinaria',
            'Usuarios ilimitados',
            'Proyectos ilimitados',
            'Soporte prioritario por WhatsApp',
            'Actualizaciones automáticas',
            'Ahorro de L. 8,625 vs plan mensual',
            'Máximo ahorro disponible',
        ]
    },
}

# Instrucciones de pago
INSTRUCCIONES_PAGO = """
Para activar tu suscripción, realiza el pago a una de nuestras cuentas bancarias:

**BAC:**
- Cuenta: 748235275
- Titular: JOKSAN HANIEL PEREZ RAMOS

**Banco de Occidente:**
- Cuenta: 21-126-003139-7
- Titular: JOKSAN HANIEL PEREZ RAMOS

**Después de realizar el pago:**
1. Envía el comprobante por WhatsApp al +504 9520-6618
2. Incluye el nombre de tu empresa y RTN
3. Tu licencia será activada en menos de 24 horas

¿Tienes dudas? Contáctanos:
- WhatsApp: +504 9520-6618
- Email: joksanhaniel@gmail.com
"""
