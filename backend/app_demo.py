from flask import Flask, jsonify, request
from flask_cors import CORS
import bcrypt
import jwt
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo-secret-key'
CORS(app, origins=['http://localhost:3000', 'http://localhost:8000'])

# Demo data
demo_users = [
    {
        'id': 1,
        'email': 'admin@admin.com',
        'hashed_password': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'name': 'Administrator',
        'role': 'admin'
    },
    {
        'id': 2,
        'email': 'user@demo.com',
        'hashed_password': bcrypt.hashpw('demo123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'name': 'Demo User',
        'role': 'user'
    }
]

demo_event_types = [
    {'id': 1, 'name': 'Concierto', 'description': 'Eventos musicales en vivo'},
    {'id': 2, 'name': 'Teatro', 'description': 'Obras teatrales y espectáculos'},
    {'id': 3, 'name': 'Deportes', 'description': 'Eventos deportivos'},
    {'id': 4, 'name': 'Conferencia', 'description': 'Conferencias y seminarios'},
    {'id': 5, 'name': 'Festival', 'description': 'Festivales y eventos culturales'}
]

demo_venues = [
    {'id': 1, 'name': 'Teatro Nacional', 'address': 'Av. Principal 123', 'city': 'Ciudad Capital', 'capacity': 2000},
    {'id': 2, 'name': 'Estadio Central', 'address': 'Zona Deportiva 456', 'city': 'Ciudad Capital', 'capacity': 50000},
    {'id': 3, 'name': 'Centro de Convenciones', 'address': 'Av. Empresarial 789', 'city': 'Ciudad Capital', 'capacity': 5000},
    {'id': 4, 'name': 'Auditorio Municipal', 'address': 'Plaza Central 321', 'city': 'Ciudad Capital', 'capacity': 1500}
]

demo_artists = [
    {'id': 1, 'name': 'Banda Rock Nacional', 'bio': 'Reconocida banda de rock con 20 años de trayectoria'},
    {'id': 2, 'name': 'Compañía de Teatro Clásico', 'bio': 'Grupo teatral especializado en obras clásicas'},
    {'id': 3, 'name': 'Orquesta Sinfónica', 'bio': 'Orquesta con músicos profesionales de renombre'},
    {'id': 4, 'name': 'DJ Internacional', 'bio': 'DJ reconocido mundialmente en música electrónica'}
]

demo_events = [
    {
        'id': 1,
        'title': 'Concierto Rock en Vivo',
        'description': 'Una noche épica de rock con los mejores éxitos',
        'event_date': '2024-02-15',
        'event_time': '20:00',
        'type_id': 1,
        'venue_id': 1,
        'artist_id': 1,
        'status': 'active',
        'event_type': 'Concierto',
        'venue_name': 'Teatro Nacional',
        'venue_city': 'Ciudad Capital',
        'artist_name': 'Banda Rock Nacional',
        'min_price': 25.00,
        'max_price': 75.00
    },
    {
        'id': 2,
        'title': 'Obra Teatral Clásica',
        'description': 'Una representación magistral de teatro clásico',
        'event_date': '2024-02-20',
        'event_time': '19:30',
        'type_id': 2,
        'venue_id': 1,
        'artist_id': 2,
        'status': 'active',
        'event_type': 'Teatro',
        'venue_name': 'Teatro Nacional',
        'venue_city': 'Ciudad Capital',
        'artist_name': 'Compañía de Teatro Clásico',
        'min_price': 30.00,
        'max_price': 60.00
    },
    {
        'id': 3,
        'title': 'Partido de Fútbol',
        'description': 'Emocionante partido de la liga local',
        'event_date': '2024-02-25',
        'event_time': '16:00',
        'type_id': 3,
        'venue_id': 2,
        'artist_id': 1,
        'status': 'active',
        'event_type': 'Deportes',
        'venue_name': 'Estadio Central',
        'venue_city': 'Ciudad Capital',
        'artist_name': 'Equipos Locales',
        'min_price': 15.00,
        'max_price': 45.00
    }
]

demo_tickets = [
    {'id': 1, 'event_id': 1, 'location': 'VIP', 'price': 75.00, 'quantity_available': 50, 'quantity_sold': 10},
    {'id': 2, 'event_id': 1, 'location': 'General', 'price': 25.00, 'quantity_available': 200, 'quantity_sold': 45},
    {'id': 3, 'event_id': 2, 'location': 'Platea', 'price': 60.00, 'quantity_available': 100, 'quantity_sold': 20},
    {'id': 4, 'event_id': 2, 'location': 'Balcón', 'price': 30.00, 'quantity_available': 150, 'quantity_sold': 35},
    {'id': 5, 'event_id': 3, 'location': 'Tribuna', 'price': 45.00, 'quantity_available': 500, 'quantity_sold': 120},
    {'id': 6, 'event_id': 3, 'location': 'General', 'price': 15.00, 'quantity_available': 1000, 'quantity_sold': 300}
]

# Helper functions
def find_user_by_email(email):
    return next((user for user in demo_users if user['email'] == email), None)

def find_user_by_id(user_id):
    return next((user for user in demo_users if user['id'] == user_id), None)

def generate_token(user):
    payload = {
        'user_id': user['id'],
        'email': user['email'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except:
        return None

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Demo API is running'}), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Event Ticketing Demo API',
        'version': '1.0.0-demo',
        'note': 'This is a demo version with mock data'
    }), 200

# Auth routes
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    user = find_user_by_email(email)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = generate_token(user)
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
    }), 200

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    
    if find_user_by_email(email):
        return jsonify({'error': 'User already exists'}), 400
    
    # In demo, just return success
    return jsonify({'message': 'User registered successfully (demo)'}), 201

@app.route('/auth/verify', methods=['GET'])
def verify():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token required'}), 401
    
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
    
    user = find_user_by_id(payload['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
    }), 200

# Events routes
@app.route('/api/events', methods=['GET'])
def get_events():
    events = demo_events.copy()
    
    # Simple filtering
    event_type = request.args.get('type')
    venue = request.args.get('venue')
    search = request.args.get('search')
    
    if event_type:
        events = [e for e in events if event_type.lower() in e['event_type'].lower()]
    
    if venue:
        events = [e for e in events if venue.lower() in e['venue_name'].lower()]
    
    if search:
        events = [e for e in events if search.lower() in e['title'].lower() or search.lower() in e['description'].lower()]
    
    return jsonify({
        'events': events,
        'pagination': {
            'page': 1,
            'per_page': 12,
            'total': len(events),
            'pages': 1
        }
    }), 200

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event_details(event_id):
    event = next((e for e in demo_events if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Get tickets for this event
    event_tickets = [t for t in demo_tickets if t['event_id'] == event_id]
    for ticket in event_tickets:
        ticket['available'] = ticket['quantity_available'] - ticket['quantity_sold']
    
    event_data = event.copy()
    event_data['tickets'] = event_tickets
    
    return jsonify(event_data), 200

@app.route('/api/event-types', methods=['GET'])
def get_event_types():
    return jsonify(demo_event_types), 200

@app.route('/api/venues', methods=['GET'])
def get_venues():
    return jsonify(demo_venues), 200

# Cart routes (simplified)
@app.route('/api/cart', methods=['GET'])
def get_cart():
    token = request.headers.get('Authorization')
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({'items': [], 'total': 0}), 200

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    token = request.headers.get('Authorization')
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({'message': 'Item added to cart (demo)'}), 200

@app.route('/api/checkout', methods=['POST'])
def checkout():
    token = request.headers.get('Authorization')
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({
        'order_id': 1,
        'payment_id': 'demo-payment-123',
        'approval_url': 'https://www.sandbox.paypal.com/demo',
        'total_amount': 50.00
    }), 200

# Admin routes
@app.route('/admin/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    token = request.headers.get('Authorization')
    payload = verify_token(token)
    if not payload or payload.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify({
        'total_events': len(demo_events),
        'active_events': len([e for e in demo_events if e['status'] == 'active']),
        'total_users': len(demo_users),
        'total_orders': 25,
        'completed_orders': 20,
        'total_revenue': 1250.00,
        'recent_orders': []
    }), 200

@app.route('/admin/events', methods=['GET'])
def get_all_events():
    token = request.headers.get('Authorization')
    payload = verify_token(token)
    if not payload or payload.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify({
        'events': demo_events,
        'pagination': {'page': 1, 'per_page': 20, 'total': len(demo_events), 'pages': 1}
    }), 200

@app.route('/admin/event-types', methods=['GET'])
def get_all_event_types():
    token = request.headers.get('Authorization')
    payload = verify_token(token)
    if not payload or payload.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify(demo_event_types), 200

@app.route('/admin/venues', methods=['GET'])
def get_all_venues():
    token = request.headers.get('Authorization')
    payload = verify_token(token)
    if not payload or payload.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify(demo_venues), 200

@app.route('/admin/artists', methods=['GET'])
def get_all_artists():
    token = request.headers.get('Authorization')
    payload = verify_token(token)
    if not payload or payload.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify(demo_artists), 200

if __name__ == '__main__':
    print("Starting Event Ticketing Demo API on port 5000")
    print("Demo credentials:")
    print("  Admin: admin@admin.com / admin123")
    print("  User: user@demo.com / demo123")
    print("Available endpoints:")
    print("  - Health check: GET /health")
    print("  - Authentication: /auth/*")
    print("  - Public API: /api/*")
    print("  - Admin API: /admin/*")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
