-- Create tables for the event ticketing system

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event types table
CREATE TABLE IF NOT EXISTS event_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Venues table
CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(255) NOT NULL,
    capacity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Artists/Hosts table
CREATE TABLE IF NOT EXISTS artists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    bio TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    event_time TIME NOT NULL,
    type_id INTEGER REFERENCES event_types(id) ON DELETE SET NULL,
    venue_id INTEGER REFERENCES venues(id) ON DELETE SET NULL,
    artist_id INTEGER REFERENCES artists(id) ON DELETE SET NULL,
    image_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tickets table (different pricing tiers for each event)
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    location VARCHAR(255) NOT NULL, -- e.g., 'VIP', 'General Admission', 'Balcony'
    price DECIMAL(10, 2) NOT NULL,
    quantity_available INTEGER NOT NULL,
    quantity_sold INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled', 'refunded')),
    total_amount DECIMAL(10, 2) NOT NULL,
    paypal_payment_id VARCHAR(255),
    paypal_payer_id VARCHAR(255)
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shopping cart table (temporary storage before order)
CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, ticket_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type_id);
CREATE INDEX IF NOT EXISTS idx_events_venue ON events(venue_id);
CREATE INDEX IF NOT EXISTS idx_tickets_event ON tickets(event_id);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_cart_user ON cart_items(user_id);

-- Insert default admin user (password: admin123)
-- Note: In production, this should be hashed properly
INSERT INTO users (email, hashed_password, name, role) 
VALUES ('admin@admin.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq9S7jS', 'Administrator', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Insert sample event types
INSERT INTO event_types (name, description) VALUES 
('Concierto', 'Eventos musicales en vivo'),
('Teatro', 'Obras teatrales y espectáculos'),
('Deportes', 'Eventos deportivos'),
('Conferencia', 'Conferencias y seminarios'),
('Festival', 'Festivales y eventos culturales')
ON CONFLICT (name) DO NOTHING;

-- Insert sample venues
INSERT INTO venues (name, address, city, capacity) VALUES 
('Teatro Nacional', 'Av. Principal 123', 'Ciudad Capital', 2000),
('Estadio Central', 'Zona Deportiva 456', 'Ciudad Capital', 50000),
('Centro de Convenciones', 'Av. Empresarial 789', 'Ciudad Capital', 5000),
('Auditorio Municipal', 'Plaza Central 321', 'Ciudad Capital', 1500)
ON CONFLICT (name) DO NOTHING;

-- Insert sample artists
INSERT INTO artists (name, bio) VALUES 
('Banda Rock Nacional', 'Reconocida banda de rock con 20 años de trayectoria'),
('Compañía de Teatro Clásico', 'Grupo teatral especializado en obras clásicas'),
('Orquesta Sinfónica', 'Orquesta con músicos profesionales de renombre'),
('DJ Internacional', 'DJ reconocido mundialmente en música electrónica')
ON CONFLICT (name) DO NOTHING;
