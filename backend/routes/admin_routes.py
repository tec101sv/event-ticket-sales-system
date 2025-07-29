from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.db import get_db
from routes.auth_routes import require_admin

admin_bp = Blueprint('admin', __name__)
db = get_db()

# Event Management
@admin_bp.route('/events', methods=['GET'])
@require_admin
def get_all_events():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        offset = (page - 1) * per_page
        
        events = db.execute_query("""
            SELECT 
                e.id, e.title, e.description, e.event_date, e.event_time, 
                e.image_url, e.status, e.created_at,
                et.name as event_type,
                v.name as venue_name,
                a.name as artist_name
            FROM events e
            LEFT JOIN event_types et ON e.type_id = et.id
            LEFT JOIN venues v ON e.venue_id = v.id
            LEFT JOIN artists a ON e.artist_id = a.id
            ORDER BY e.created_at DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset), fetch=True)
        
        total_count = db.execute_query("SELECT COUNT(*) FROM events", fetch='one')['count']
        
        return jsonify({
            'events': events or [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"Get all events error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/events', methods=['POST'])
@require_admin
def create_event():
    try:
        data = request.get_json()
        
        required_fields = ['title', 'description', 'event_date', 'event_time', 'type_id', 'venue_id', 'artist_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        event_id = db.execute_query("""
            INSERT INTO events (title, description, event_date, event_time, type_id, venue_id, artist_id, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['title'], data['description'], data['event_date'], data['event_time'],
            data['type_id'], data['venue_id'], data['artist_id'], data.get('image_url')
        ), fetch='one')['id']
        
        # Add tickets if provided
        if data.get('tickets'):
            for ticket in data['tickets']:
                db.execute_query("""
                    INSERT INTO tickets (event_id, location, price, quantity_available)
                    VALUES (%s, %s, %s, %s)
                """, (event_id, ticket['location'], ticket['price'], ticket['quantity']))
        
        return jsonify({'message': 'Event created successfully', 'event_id': event_id}), 201
        
    except Exception as e:
        print(f"Create event error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/events/<int:event_id>', methods=['GET'])
@require_admin
def get_event_admin(event_id):
    try:
        event = db.execute_query("""
            SELECT 
                e.id, e.title, e.description, e.event_date, e.event_time, 
                e.type_id, e.venue_id, e.artist_id, e.image_url, e.status,
                et.name as event_type,
                v.name as venue_name,
                a.name as artist_name
            FROM events e
            LEFT JOIN event_types et ON e.type_id = et.id
            LEFT JOIN venues v ON e.venue_id = v.id
            LEFT JOIN artists a ON e.artist_id = a.id
            WHERE e.id = %s
        """, (event_id,), fetch='one')
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        tickets = db.execute_query("""
            SELECT id, location, price, quantity_available, quantity_sold
            FROM tickets WHERE event_id = %s ORDER BY price ASC
        """, (event_id,), fetch=True)
        
        event_data = dict(event)
        event_data['tickets'] = tickets or []
        
        return jsonify(event_data), 200
        
    except Exception as e:
        print(f"Get event admin error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/events/<int:event_id>', methods=['PUT'])
@require_admin
def update_event(event_id):
    try:
        data = request.get_json()
        
        # Check if event exists
        existing_event = db.execute_query("SELECT id FROM events WHERE id = %s", (event_id,), fetch='one')
        if not existing_event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Update event
        db.execute_query("""
            UPDATE events 
            SET title = %s, description = %s, event_date = %s, event_time = %s,
                type_id = %s, venue_id = %s, artist_id = %s, image_url = %s, status = %s
            WHERE id = %s
        """, (
            data.get('title'), data.get('description'), data.get('event_date'), 
            data.get('event_time'), data.get('type_id'), data.get('venue_id'),
            data.get('artist_id'), data.get('image_url'), data.get('status', 'active'),
            event_id
        ))
        
        # Update tickets if provided
        if data.get('tickets'):
            # Delete existing tickets
            db.execute_query("DELETE FROM tickets WHERE event_id = %s", (event_id,))
            
            # Add new tickets
            for ticket in data['tickets']:
                db.execute_query("""
                    INSERT INTO tickets (event_id, location, price, quantity_available)
                    VALUES (%s, %s, %s, %s)
                """, (event_id, ticket['location'], ticket['price'], ticket['quantity']))
        
        return jsonify({'message': 'Event updated successfully'}), 200
        
    except Exception as e:
        print(f"Update event error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/events/<int:event_id>', methods=['DELETE'])
@require_admin
def delete_event(event_id):
    try:
        # Check if event exists
        existing_event = db.execute_query("SELECT id FROM events WHERE id = %s", (event_id,), fetch='one')
        if not existing_event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Delete event (cascade will handle tickets)
        db.execute_query("DELETE FROM events WHERE id = %s", (event_id,))
        
        return jsonify({'message': 'Event deleted successfully'}), 200
        
    except Exception as e:
        print(f"Delete event error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Event Types Management
@admin_bp.route('/event-types', methods=['GET'])
@require_admin
def get_all_event_types():
    try:
        event_types = db.execute_query("""
            SELECT id, name, description, created_at
            FROM event_types ORDER BY name
        """, fetch=True)
        
        return jsonify(event_types or []), 200
        
    except Exception as e:
        print(f"Get event types error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/event-types', methods=['POST'])
@require_admin
def create_event_type():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        event_type_id = db.execute_query("""
            INSERT INTO event_types (name, description)
            VALUES (%s, %s) RETURNING id
        """, (data['name'], data.get('description')), fetch='one')['id']
        
        return jsonify({'message': 'Event type created successfully', 'id': event_type_id}), 201
        
    except Exception as e:
        print(f"Create event type error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/event-types/<int:type_id>', methods=['PUT'])
@require_admin
def update_event_type(type_id):
    try:
        data = request.get_json()
        
        # Check if event type exists
        existing_type = db.execute_query("SELECT id FROM event_types WHERE id = %s", (type_id,), fetch='one')
        if not existing_type:
            return jsonify({'error': 'Event type not found'}), 404
        
        db.execute_query("""
            UPDATE event_types 
            SET name = %s, description = %s
            WHERE id = %s
        """, (data.get('name'), data.get('description'), type_id))
        
        return jsonify({'message': 'Event type updated successfully'}), 200
        
    except Exception as e:
        print(f"Update event type error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/event-types/<int:type_id>', methods=['DELETE'])
@require_admin
def delete_event_type(type_id):
    try:
        # Check if event type exists
        existing_type = db.execute_query("SELECT id FROM event_types WHERE id = %s", (type_id,), fetch='one')
        if not existing_type:
            return jsonify({'error': 'Event type not found'}), 404
        
        db.execute_query("DELETE FROM event_types WHERE id = %s", (type_id,))
        
        return jsonify({'message': 'Event type deleted successfully'}), 200
        
    except Exception as e:
        print(f"Delete event type error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Venues Management
@admin_bp.route('/venues', methods=['GET'])
@require_admin
def get_all_venues():
    try:
        venues = db.execute_query("""
            SELECT id, name, address, city, capacity, created_at
            FROM venues ORDER BY name
        """, fetch=True)
        
        return jsonify(venues or []), 200
        
    except Exception as e:
        print(f"Get venues error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/venues', methods=['POST'])
@require_admin
def create_venue():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'address', 'city']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        venue_id = db.execute_query("""
            INSERT INTO venues (name, address, city, capacity)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (data['name'], data['address'], data['city'], data.get('capacity')), fetch='one')['id']
        
        return jsonify({'message': 'Venue created successfully', 'id': venue_id}), 201
        
    except Exception as e:
        print(f"Create venue error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/venues/<int:venue_id>', methods=['PUT'])
@require_admin
def update_venue(venue_id):
    try:
        data = request.get_json()
        
        # Check if venue exists
        existing_venue = db.execute_query("SELECT id FROM venues WHERE id = %s", (venue_id,), fetch='one')
        if not existing_venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        db.execute_query("""
            UPDATE venues 
            SET name = %s, address = %s, city = %s, capacity = %s
            WHERE id = %s
        """, (data.get('name'), data.get('address'), data.get('city'), data.get('capacity'), venue_id))
        
        return jsonify({'message': 'Venue updated successfully'}), 200
        
    except Exception as e:
        print(f"Update venue error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/venues/<int:venue_id>', methods=['DELETE'])
@require_admin
def delete_venue(venue_id):
    try:
        # Check if venue exists
        existing_venue = db.execute_query("SELECT id FROM venues WHERE id = %s", (venue_id,), fetch='one')
        if not existing_venue:
            return jsonify({'error': 'Venue not found'}), 404
        
        db.execute_query("DELETE FROM venues WHERE id = %s", (venue_id,))
        
        return jsonify({'message': 'Venue deleted successfully'}), 200
        
    except Exception as e:
        print(f"Delete venue error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Artists Management
@admin_bp.route('/artists', methods=['GET'])
@require_admin
def get_all_artists():
    try:
        artists = db.execute_query("""
            SELECT id, name, bio, image_url, created_at
            FROM artists ORDER BY name
        """, fetch=True)
        
        return jsonify(artists or []), 200
        
    except Exception as e:
        print(f"Get artists error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/artists', methods=['POST'])
@require_admin
def create_artist():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        artist_id = db.execute_query("""
            INSERT INTO artists (name, bio, image_url)
            VALUES (%s, %s, %s) RETURNING id
        """, (data['name'], data.get('bio'), data.get('image_url')), fetch='one')['id']
        
        return jsonify({'message': 'Artist created successfully', 'id': artist_id}), 201
        
    except Exception as e:
        print(f"Create artist error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/artists/<int:artist_id>', methods=['PUT'])
@require_admin
def update_artist(artist_id):
    try:
        data = request.get_json()
        
        # Check if artist exists
        existing_artist = db.execute_query("SELECT id FROM artists WHERE id = %s", (artist_id,), fetch='one')
        if not existing_artist:
            return jsonify({'error': 'Artist not found'}), 404
        
        db.execute_query("""
            UPDATE artists 
            SET name = %s, bio = %s, image_url = %s
            WHERE id = %s
        """, (data.get('name'), data.get('bio'), data.get('image_url'), artist_id))
        
        return jsonify({'message': 'Artist updated successfully'}), 200
        
    except Exception as e:
        print(f"Update artist error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/artists/<int:artist_id>', methods=['DELETE'])
@require_admin
def delete_artist(artist_id):
    try:
        # Check if artist exists
        existing_artist = db.execute_query("SELECT id FROM artists WHERE id = %s", (artist_id,), fetch='one')
        if not existing_artist:
            return jsonify({'error': 'Artist not found'}), 404
        
        db.execute_query("DELETE FROM artists WHERE id = %s", (artist_id,))
        
        return jsonify({'message': 'Artist deleted successfully'}), 200
        
    except Exception as e:
        print(f"Delete artist error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Dashboard Statistics
@admin_bp.route('/dashboard/stats', methods=['GET'])
@require_admin
def get_dashboard_stats():
    try:
        # Get various statistics
        stats = {}
        
        # Total events
        stats['total_events'] = db.execute_query("SELECT COUNT(*) FROM events", fetch='one')['count']
        
        # Active events
        stats['active_events'] = db.execute_query(
            "SELECT COUNT(*) FROM events WHERE status = 'active' AND event_date >= CURRENT_DATE", 
            fetch='one'
        )['count']
        
        # Total users
        stats['total_users'] = db.execute_query("SELECT COUNT(*) FROM users WHERE role = 'user'", fetch='one')['count']
        
        # Total orders
        stats['total_orders'] = db.execute_query("SELECT COUNT(*) FROM orders", fetch='one')['count']
        
        # Completed orders
        stats['completed_orders'] = db.execute_query(
            "SELECT COUNT(*) FROM orders WHERE status = 'completed'", 
            fetch='one'
        )['count']
        
        # Total revenue
        revenue_result = db.execute_query(
            "SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE status = 'completed'", 
            fetch='one'
        )
        stats['total_revenue'] = float(revenue_result['coalesce'])
        
        # Recent orders
        recent_orders = db.execute_query("""
            SELECT 
                o.id, o.order_date, o.total_amount, o.status,
                u.name as user_name, u.email as user_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.order_date DESC
            LIMIT 10
        """, fetch=True)
        
        stats['recent_orders'] = recent_orders or []
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Get dashboard stats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Orders Management
@admin_bp.route('/orders', methods=['GET'])
@require_admin
def get_all_orders():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status')
        
        offset = (page - 1) * per_page
        
        query = """
            SELECT 
                o.id, o.order_date, o.status, o.total_amount,
                u.name as user_name, u.email as user_email,
                COUNT(oi.id) as total_tickets
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
        """
        
        params = []
        if status:
            query += " WHERE o.status = %s"
            params.append(status)
        
        query += """
            GROUP BY o.id, o.order_date, o.status, o.total_amount, u.name, u.email
            ORDER BY o.order_date DESC
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        
        orders = db.execute_query(query, params, fetch=True)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM orders"
        count_params = []
        if status:
            count_query += " WHERE status = %s"
            count_params.append(status)
        
        total_count = db.execute_query(count_query, count_params, fetch='one')['count']
        
        return jsonify({
            'orders': orders or [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"Get all orders error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
