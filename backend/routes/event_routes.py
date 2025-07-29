from flask import Blueprint, request, jsonify
from datetime import datetime, date
from utils.db import get_db
from utils.paypal_integration import paypal
from routes.auth_routes import require_auth

event_bp = Blueprint('events', __name__)
db = get_db()

@event_bp.route('/events', methods=['GET'])
def get_events():
    try:
        # Get all events using Supabase API
        events_data = db.execute_query('events')
        
        # Get related data
        event_types = {et['id']: et for et in db.execute_query('event_types')}
        venues = {v['id']: v for v in db.execute_query('venues')}
        artists = {a['id']: a for a in db.execute_query('artists')}
        tickets = db.execute_query('tickets')
        
        # Process events
        events = []
        for event in events_data:
            if event['status'] == 'active':
                # Get related data
                event_type = event_types.get(event['type_id'], {})
                venue = venues.get(event['venue_id'], {})
                artist = artists.get(event['artist_id'], {})
                
                # Get ticket prices for this event
                event_tickets = [t for t in tickets if t['event_id'] == event['id']]
                prices = [t['price'] for t in event_tickets] if event_tickets else [0]
                
                processed_event = {
                    'id': event['id'],
                    'title': event['title'],
                    'description': event['description'],
                    'event_date': event['event_date'],
                    'event_time': event['event_time'],
                    'image_url': event['image_url'],
                    'status': event['status'],
                    'event_type': event_type.get('name', ''),
                    'venue_name': venue.get('name', ''),
                    'venue_city': venue.get('city', ''),
                    'artist_name': artist.get('name', ''),
                    'min_price': min(prices) if prices else 0,
                    'max_price': max(prices) if prices else 0
                }
                events.append(processed_event)
        
        # Sort by date
        events.sort(key=lambda x: x['event_date'])
        
        return jsonify({
            'events': events,
            'pagination': {
                'page': 1,
                'per_page': len(events),
                'total': len(events),
                'pages': 1
            }
        }), 200
        
    except Exception as e:
        print(f"Get events error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event_details(event_id):
    try:
        # Get event details
        event = db.execute_query("""
            SELECT 
                e.id, e.title, e.description, e.event_date, e.event_time, 
                e.image_url, e.status,
                et.name as event_type, et.description as type_description,
                v.name as venue_name, v.address as venue_address, 
                v.city as venue_city, v.capacity as venue_capacity,
                a.name as artist_name, a.bio as artist_bio, a.image_url as artist_image
            FROM events e
            LEFT JOIN event_types et ON e.type_id = et.id
            LEFT JOIN venues v ON e.venue_id = v.id
            LEFT JOIN artists a ON e.artist_id = a.id
            WHERE e.id = %s AND e.status = 'active'
        """, (event_id,), fetch='one')
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Get available tickets
        tickets = db.execute_query("""
            SELECT 
                id, location, price, quantity_available, quantity_sold,
                (quantity_available - quantity_sold) as available
            FROM tickets 
            WHERE event_id = %s AND (quantity_available - quantity_sold) > 0
            ORDER BY price ASC
        """, (event_id,), fetch=True)
        
        event_data = dict(event)
        event_data['tickets'] = tickets or []
        
        return jsonify(event_data), 200
        
    except Exception as e:
        print(f"Get event details error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/event-types', methods=['GET'])
def get_event_types():
    try:
        event_types = db.execute_query(
            "SELECT id, name, description FROM event_types ORDER BY name",
            fetch=True
        )
        return jsonify(event_types or []), 200
        
    except Exception as e:
        print(f"Get event types error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/venues', methods=['GET'])
def get_venues():
    try:
        venues = db.execute_query(
            "SELECT id, name, city FROM venues ORDER BY name",
            fetch=True
        )
        return jsonify(venues or []), 200
        
    except Exception as e:
        print(f"Get venues error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/cart', methods=['GET'])
@require_auth
def get_cart():
    try:
        user_id = request.user['user_id']
        
        cart_items = db.execute_query("""
            SELECT 
                ci.id, ci.quantity,
                t.id as ticket_id, t.location, t.price,
                e.id as event_id, e.title as event_title, 
                e.event_date, e.event_time,
                v.name as venue_name
            FROM cart_items ci
            JOIN tickets t ON ci.ticket_id = t.id
            JOIN events e ON t.event_id = e.id
            JOIN venues v ON e.venue_id = v.id
            WHERE ci.user_id = %s
            ORDER BY ci.created_at DESC
        """, (user_id,), fetch=True)
        
        total = sum(item['price'] * item['quantity'] for item in cart_items or [])
        
        return jsonify({
            'items': cart_items or [],
            'total': float(total)
        }), 200
        
    except Exception as e:
        print(f"Get cart error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/cart', methods=['POST'])
@require_auth
def add_to_cart():
    try:
        user_id = request.user['user_id']
        data = request.get_json()
        
        ticket_id = data.get('ticket_id')
        quantity = data.get('quantity', 1)
        
        if not ticket_id or quantity <= 0:
            return jsonify({'error': 'Invalid ticket_id or quantity'}), 400
        
        # Check if ticket exists and has availability
        ticket = db.execute_query("""
            SELECT id, event_id, location, price, quantity_available, quantity_sold
            FROM tickets 
            WHERE id = %s
        """, (ticket_id,), fetch='one')
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        available = ticket['quantity_available'] - ticket['quantity_sold']
        if available < quantity:
            return jsonify({'error': f'Only {available} tickets available'}), 400
        
        # Check if item already in cart
        existing_item = db.execute_query("""
            SELECT id, quantity FROM cart_items 
            WHERE user_id = %s AND ticket_id = %s
        """, (user_id, ticket_id), fetch='one')
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item['quantity'] + quantity
            if available < new_quantity:
                return jsonify({'error': f'Only {available} tickets available'}), 400
            
            db.execute_query("""
                UPDATE cart_items SET quantity = %s 
                WHERE user_id = %s AND ticket_id = %s
            """, (new_quantity, user_id, ticket_id))
        else:
            # Add new item
            db.execute_query("""
                INSERT INTO cart_items (user_id, ticket_id, quantity) 
                VALUES (%s, %s, %s)
            """, (user_id, ticket_id, quantity))
        
        return jsonify({'message': 'Item added to cart successfully'}), 200
        
    except Exception as e:
        print(f"Add to cart error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/cart/<int:item_id>', methods=['DELETE'])
@require_auth
def remove_from_cart(item_id):
    try:
        user_id = request.user['user_id']
        
        db.execute_query("""
            DELETE FROM cart_items 
            WHERE id = %s AND user_id = %s
        """, (item_id, user_id))
        
        return jsonify({'message': 'Item removed from cart'}), 200
        
    except Exception as e:
        print(f"Remove from cart error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/checkout', methods=['POST'])
@require_auth
def checkout():
    try:
        user_id = request.user['user_id']
        
        # Get cart items
        cart_items = db.execute_query("""
            SELECT 
                ci.id, ci.quantity,
                t.id as ticket_id, t.price, t.quantity_available, t.quantity_sold
            FROM cart_items ci
            JOIN tickets t ON ci.ticket_id = t.id
            WHERE ci.user_id = %s
        """, (user_id,), fetch=True)
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Validate availability and calculate total
        total_amount = 0
        for item in cart_items:
            available = item['quantity_available'] - item['quantity_sold']
            if available < item['quantity']:
                return jsonify({'error': f'Insufficient tickets available'}), 400
            total_amount += item['price'] * item['quantity']
        
        # Create PayPal payment
        payment = paypal.create_payment(
            amount=total_amount,
            return_url="http://localhost:3000/payment/success",
            cancel_url="http://localhost:3000/payment/cancel"
        )
        
        if not payment:
            return jsonify({'error': 'Failed to create payment'}), 500
        
        # Create order in database
        order_id = db.execute_query("""
            INSERT INTO orders (user_id, total_amount, status, paypal_payment_id) 
            VALUES (%s, %s, 'pending', %s) RETURNING id
        """, (user_id, total_amount, payment['id']), fetch='one')['id']
        
        # Create order items
        for item in cart_items:
            db.execute_query("""
                INSERT INTO order_items (order_id, ticket_id, quantity, price) 
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['ticket_id'], item['quantity'], item['price']))
        
        return jsonify({
            'order_id': order_id,
            'payment_id': payment['id'],
            'approval_url': payment.get('approval_url'),
            'total_amount': float(total_amount)
        }), 200
        
    except Exception as e:
        print(f"Checkout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/payment/execute', methods=['POST'])
@require_auth
def execute_payment():
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')
        payer_id = data.get('payer_id')
        
        if not payment_id or not payer_id:
            return jsonify({'error': 'Payment ID and Payer ID are required'}), 400
        
        # Execute PayPal payment
        result = paypal.execute_payment(payment_id, payer_id)
        
        if not result or result.get('state') != 'approved':
            return jsonify({'error': 'Payment execution failed'}), 400
        
        # Update order status
        db.execute_query("""
            UPDATE orders 
            SET status = 'completed', paypal_payer_id = %s 
            WHERE paypal_payment_id = %s
        """, (payer_id, payment_id))
        
        # Update ticket quantities and clear cart
        user_id = request.user['user_id']
        
        # Get order items to update ticket quantities
        order_items = db.execute_query("""
            SELECT oi.ticket_id, oi.quantity
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.paypal_payment_id = %s
        """, (payment_id,), fetch=True)
        
        for item in order_items:
            db.execute_query("""
                UPDATE tickets 
                SET quantity_sold = quantity_sold + %s 
                WHERE id = %s
            """, (item['quantity'], item['ticket_id']))
        
        # Clear user's cart
        db.execute_query("DELETE FROM cart_items WHERE user_id = %s", (user_id,))
        
        return jsonify({'message': 'Payment completed successfully'}), 200
        
    except Exception as e:
        print(f"Execute payment error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/orders', methods=['GET'])
@require_auth
def get_user_orders():
    try:
        user_id = request.user['user_id']
        
        orders = db.execute_query("""
            SELECT 
                o.id, o.order_date, o.status, o.total_amount,
                COUNT(oi.id) as total_tickets
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = %s
            GROUP BY o.id, o.order_date, o.status, o.total_amount
            ORDER BY o.order_date DESC
        """, (user_id,), fetch=True)
        
        return jsonify(orders or []), 200
        
    except Exception as e:
        print(f"Get user orders error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@event_bp.route('/orders/<int:order_id>', methods=['GET'])
@require_auth
def get_order_details(order_id):
    try:
        user_id = request.user['user_id']
        
        # Get order details
        order = db.execute_query("""
            SELECT id, order_date, status, total_amount
            FROM orders 
            WHERE id = %s AND user_id = %s
        """, (order_id, user_id), fetch='one')
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Get order items
        items = db.execute_query("""
            SELECT 
                oi.quantity, oi.price,
                t.location,
                e.title as event_title, e.event_date, e.event_time,
                v.name as venue_name
            FROM order_items oi
            JOIN tickets t ON oi.ticket_id = t.id
            JOIN events e ON t.event_id = e.id
            JOIN venues v ON e.venue_id = v.id
            WHERE oi.order_id = %s
        """, (order_id,), fetch=True)
        
        order_data = dict(order)
        order_data['items'] = items or []
        
        return jsonify(order_data), 200
        
    except Exception as e:
        print(f"Get order details error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
