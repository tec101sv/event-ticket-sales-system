# EventTickets - Sistema de Venta de Tickets para Eventos

Una aplicación web completa para la venta de tickets de eventos, similar a Ticketmaster, construida con React (frontend), Flask (backend) y PostgreSQL con Supabase.

## 🚀 Características

### Sitio Web Público
- **Navegación de eventos**: Grid de eventos próximos con información detallada
- **Búsqueda y filtros**: Por tipo de evento, lugar, fecha y búsqueda de texto
- **Registro y autenticación**: Sistema completo de usuarios
- **Carrito de compras**: Agregar múltiples tickets y gestionar compras
- **Pago seguro**: Integración con PayPal para pagos internacionales
- **Responsive**: Diseño adaptable a todos los dispositivos

### Panel de Administración
- **Dashboard**: Estadísticas y métricas del sistema
- **Gestión de eventos**: CRUD completo con múltiples tipos de tickets
- **Gestión de lugares**: Administrar venues y ubicaciones
- **Gestión de artistas**: Administrar artistas y anfitriones
- **Gestión de tipos**: Categorías de eventos personalizables
- **Órdenes**: Visualización y gestión de todas las ventas

### Características Técnicas
- **Frontend**: React 18 con Tailwind CSS
- **Backend**: Flask con arquitectura RESTful
- **Base de datos**: PostgreSQL con Supabase
- **Autenticación**: JWT tokens
- **Pagos**: Integración PayPal
- **Responsive**: Diseño mobile-first

## 📋 Requisitos Previos

- Node.js 16+ y npm
- Python 3.8+
- Cuenta de Supabase (gratuita)
- Cuenta de PayPal Developer (para pagos)

## 🛠️ Instalación

### 1. Configurar el Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Edita el archivo `backend/.env`:

```env
# Database Configuration
SUPABASE_DB_PASSWORD=tu_password_de_supabase

# Flask Configuration
SECRET_KEY=tu-clave-secreta-super-segura
JWT_SECRET_KEY=tu-jwt-clave-secreta

# PayPal Configuration (Sandbox para desarrollo)
PAYPAL_CLIENT_ID=tu_paypal_client_id
PAYPAL_SECRET=tu_paypal_secret
PAYPAL_MODE=sandbox
```

### 3. Configurar Supabase

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta
2. Crea un nuevo proyecto
3. Ve a Settings > Database y obtén tu password
4. Actualiza el archivo `.env` con tu password de Supabase

### 4. Configurar PayPal

1. Ve a [developer.paypal.com](https://developer.paypal.com)
2. Crea una aplicación en modo Sandbox
3. Obtén tu Client ID y Secret
4. Actualiza el archivo `.env` con tus credenciales

### 5. Inicializar la Base de Datos

```bash
cd backend
python app.py
```

### 6. Configurar el Frontend

```bash
cd frontend
npm install
```

## 🚀 Ejecutar la Aplicación

### Iniciar el Backend
```bash
cd backend
python app.py
```
Backend disponible en: `http://localhost:5000`

### Iniciar el Frontend
```bash
cd frontend
npm start
```
Frontend disponible en: `http://localhost:3000`

## 👤 Credenciales de Acceso

### Usuario Administrador
- **Email**: admin@admin.com
- **Contraseña**: admin123

### Usuarios Regulares
- Regístrate desde la interfaz web

## 📱 Uso de la Aplicación

### Para Usuarios
1. Explorar eventos disponibles
2. Buscar y filtrar eventos
3. Registrarse para comprar tickets
4. Agregar tickets al carrito
5. Completar compra con PayPal

### Para Administradores
1. Acceder al panel de administración
2. Gestionar eventos, lugares, artistas y tipos
3. Configurar tickets con precios y ubicaciones
4. Monitorear ventas y estadísticas

## 🏗️ Estructura del Proyecto

```
project/
├── backend/                 # API Flask
│   ├── routes/             # Endpoints de la API
│   ├── utils/              # Utilidades (DB, PayPal)
│   ├── migrations/         # Scripts de base de datos
│   ├── app.py             # Aplicación principal
│   └── config.py          # Configuración
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── services/      # Servicios API
│   │   └── App.js         # Componente principal
│   └── public/            # Archivos estáticos
└── README.md
```

## 🔧 API Endpoints Principales

### Autenticación
- `POST /auth/register` - Registro de usuario
- `POST /auth/login` - Inicio de sesión
- `GET /auth/verify` - Verificar token

### Eventos Públicos
- `GET /api/events` - Listar eventos
- `GET /api/events/{id}` - Detalles del evento
- `POST /api/cart` - Agregar al carrito
- `POST /api/checkout` - Procesar pago

### Administración
- `GET /admin/dashboard/stats` - Estadísticas
- `POST /admin/events` - Crear evento
- `GET /admin/venues` - Gestión de lugares
- `GET /admin/artists` - Gestión de artistas

## 🎯 Funcionalidades Implementadas

✅ **Frontend React completo**
- Listado de eventos con grid responsive
- Búsqueda y filtros avanzados
- Sistema de autenticación
- Carrito de compras funcional
- Panel de administración completo

✅ **Backend Flask robusto**
- API RESTful completa
- Autenticación JWT
- Integración con Supabase
- Integración con PayPal
- Sistema de roles (admin/usuario)

✅ **Base de datos PostgreSQL**
- Esquema completo con relaciones
- Datos de ejemplo incluidos
- Migraciones automáticas

✅ **Características adicionales**
- Diseño similar a Ticketmaster
- Responsive design con Tailwind CSS
- Manejo de errores robusto
- Validaciones de seguridad

---

**¡Tu plataforma de venta de tickets está lista! 🎫**

Para comenzar, configura las variables de entorno y ejecuta tanto el backend como el frontend siguiendo las instrucciones de instalación.
