#!/usr/bin/env python3
"""
Script para inicializar la base de datos con las tablas necesarias
y datos de ejemplo para la aplicación EventTickets
"""

import os
import sys
from utils.db import supabase_db
from config import Config

def create_tables():
    """Crear todas las tablas necesarias"""
    
    # SQL para crear las tablas
    create_tables_sql = """
    -- Crear tabla de usuarios
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20),
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear tabla de tipos de eventos
    CREATE TABLE IF NOT EXISTS event_types (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear tabla de lugares/venues
    CREATE TABLE IF NOT EXISTS venues (
        id SERIAL PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        address TEXT NOT NULL,
        city VARCHAR(100) NOT NULL,
        state VARCHAR(100),
        country VARCHAR(100) NOT NULL,
        capacity INTEGER,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear tabla de artistas
    CREATE TABLE IF NOT EXISTS artists (
        id SERIAL PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        bio TEXT,
        genre VARCHAR(100),
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear tabla de eventos
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        event_date TIMESTAMP NOT NULL,
        event_type_id INTEGER REFERENCES event_types(id),
        venue_id INTEGER REFERENCES venues(id),
        artist_id INTEGER REFERENCES artists(id),
        image_url TEXT,
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear tabla de tipos de tickets
    CREATE TABLE IF NOT EXISTS ticket_types (
        id SERIAL PRIMARY KEY,
        event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        quantity_available INTEGER NOT NULL,
        quantity_sold INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear tabla de carrito de compras
    CREATE TABLE IF NOT EXISTS cart_items (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        ticket_type_id INTEGER REFERENCES ticket_types(id) ON DELETE CASCADE,
        quantity INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear tabla de órdenes
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        total_amount DECIMAL(10,2) NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        payment_id VARCHAR(255),
        payment_method VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear tabla de items de órdenes
    CREATE TABLE IF NOT EXISTS order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
        ticket_type_id INTEGER REFERENCES ticket_types(id),
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        total_price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Crear índices para mejorar performance
    CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
    CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type_id);
    CREATE INDEX IF NOT EXISTS idx_events_venue ON events(venue_id);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
    CREATE INDEX IF NOT EXISTS idx_cart_user ON cart_items(user_id);
    """
    
    try:
        print("Creando tablas...")
        supabase_db.execute_query(create_tables_sql)
        print("✅ Tablas creadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

def create_admin_user():
    """Crear usuario administrador por defecto"""
    
    import bcrypt
    
    # Hash de la contraseña admin123
    password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    insert_admin_sql = """
    INSERT INTO users (email, password_hash, first_name, last_name, is_admin)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (email) DO NOTHING
    """
    
    try:
        print("Creando usuario administrador...")
        supabase_db.execute_query(
            insert_admin_sql, 
            ('admin@admin.com', password_hash, 'Admin', 'User', True)
        )
        print("✅ Usuario administrador creado: admin@admin.com / admin123")
        return True
    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")
        return False

def create_sample_data():
    """Crear datos de ejemplo"""
    
    try:
        print("Creando datos de ejemplo...")
        
        # Tipos de eventos
        event_types_sql = """
        INSERT INTO event_types (name, description) VALUES
        ('Concierto', 'Eventos musicales en vivo'),
        ('Teatro', 'Obras de teatro y espectáculos'),
        ('Deportes', 'Eventos deportivos'),
        ('Conferencia', 'Conferencias y seminarios'),
        ('Festival', 'Festivales y eventos culturales')
        ON CONFLICT DO NOTHING
        """
        
        # Venues
        venues_sql = """
        INSERT INTO venues (name, address, city, country, capacity) VALUES
        ('Teatro Nacional', 'Av. Principal 123', 'Ciudad de México', 'México', 2000),
        ('Estadio Central', 'Calle Deportiva 456', 'Guadalajara', 'México', 50000),
        ('Centro de Convenciones', 'Blvd. Empresarial 789', 'Monterrey', 'México', 5000),
        ('Auditorio Municipal', 'Plaza Central 321', 'Puebla', 'México', 1500),
        ('Arena Deportiva', 'Av. Olímpica 654', 'Tijuana', 'México', 15000)
        ON CONFLICT DO NOTHING
        """
        
        # Artistas
        artists_sql = """
        INSERT INTO artists (name, bio, genre) VALUES
        ('Los Rockeros', 'Banda de rock mexicano con 20 años de trayectoria', 'Rock'),
        ('María González', 'Cantante de música popular mexicana', 'Pop Latino'),
        ('Compañía de Teatro Clásico', 'Grupo teatral especializado en obras clásicas', 'Teatro'),
        ('Orquesta Sinfónica Nacional', 'La mejor orquesta del país', 'Clásica'),
        ('DJ ElectroMex', 'DJ especializado en música electrónica', 'Electrónica')
        ON CONFLICT DO NOTHING
        """
        
        supabase_db.execute_query(event_types_sql)
        supabase_db.execute_query(venues_sql)
        supabase_db.execute_query(artists_sql)
        
        print("✅ Datos de ejemplo creados exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando datos de ejemplo: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Inicializando base de datos EventTickets...")
    print(f"📍 Conectando a: {Config.SUPABASE_URL}")
    
    success = True
    
    # Crear tablas
    if not create_tables():
        success = False
    
    # Crear usuario admin
    if not create_admin_user():
        success = False
    
    # Crear datos de ejemplo
    if not create_sample_data():
        success = False
    
    if success:
        print("\n🎉 ¡Base de datos inicializada exitosamente!")
        print("\n📋 Credenciales de administrador:")
        print("   Email: admin@admin.com")
        print("   Contraseña: admin123")
    else:
        print("\n❌ Hubo errores durante la inicialización")
        sys.exit(1)

if __name__ == "__main__":
    main()
