#!/usr/bin/env python3
"""
Script to create sample events for testing
"""
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_db

def create_sample_events():
    """Create sample events with tickets"""
    print("Creating sample events...")
    
    try:
        db = get_db()
        
        # Sample events data
        events_data = [
            {
                'title': 'Concierto de Rock Nacional',
                'description': 'Una noche épica con la mejor banda de rock del país. Prepárate para una experiencia musical inolvidable con todos sus grandes éxitos.',
                'event_date': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
                'event_time': '20:00:00',
                'type_id': 1,  # Concierto
                'venue_id': 1,  # Teatro Nacional
                'artist_id': 1,  # Banda Rock Nacional
                'image_url': 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800',
                'status': 'active'
            },
            {
                'title': 'Obra de Teatro Clásico',
                'description': 'Una representación magistral de una obra clásica interpretada por los mejores actores del país. Una experiencia cultural única.',
                'event_date': (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d'),
                'event_time': '19:30:00',
                'type_id': 2,  # Teatro
                'venue_id': 1,  # Teatro Nacional
                'artist_id': 2,  # Compañía de Teatro Clásico
                'image_url': 'https://images.unsplash.com/photo-1507924538820-ede94a04019d?w=800',
                'status': 'active'
            },
            {
                'title': 'Concierto Sinfónico',
                'description': 'Una velada musical extraordinaria con la orquesta sinfónica interpretando las mejores piezas clásicas y contemporáneas.',
                'event_date': (datetime.now() + timedelta(days=22)).strftime('%Y-%m-%d'),
                'event_time': '18:00:00',
                'type_id': 1,  # Concierto
                'venue_id': 1,  # Teatro Nacional
                'artist_id': 3,  # Orquesta Sinfónica
                'image_url': 'https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800',
                'status': 'active'
            },
            {
                'title': 'Festival de Música Electrónica',
                'description': 'La mejor música electrónica con DJ internacional. Una noche de baile y diversión que no puedes perderte.',
                'event_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'event_time': '21:00:00',
                'type_id': 5,  # Festival
                'venue_id': 3,  # Centro de Convenciones
                'artist_id': 4,  # DJ Internacional
                'image_url': 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800',
                'status': 'active'
            },
            {
                'title': 'Conferencia de Tecnología',
                'description': 'Los mejores expertos en tecnología compartirán las últimas tendencias e innovaciones del sector.',
                'event_date': (datetime.now() + timedelta(days=12)).strftime('%Y-%m-%d'),
                'event_time': '09:00:00',
                'type_id': 4,  # Conferencia
                'venue_id': 3,  # Centro de Convenciones
                'artist_id': 1,  # Usando artista existente
                'image_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800',
                'status': 'active'
            }
        ]
        
        # Create events
        created_events = []
        for event_data in events_data:
            try:
                event = db.execute_query('events', 'insert', event_data)
                created_events.append(event[0])
                print(f"✅ Created event: {event_data['title']}")
            except Exception as e:
                print(f"❌ Error creating event {event_data['title']}: {e}")
        
        # Create tickets for each event
        tickets_data = [
            # Concierto de Rock Nacional
            [
                {'event_id': 1, 'location': 'VIP', 'price': 150.00, 'quantity_available': 50, 'quantity_sold': 0},
                {'event_id': 1, 'location': 'Platea', 'price': 80.00, 'quantity_available': 200, 'quantity_sold': 0},
                {'event_id': 1, 'location': 'Balcón', 'price': 45.00, 'quantity_available': 300, 'quantity_sold': 0}
            ],
            # Obra de Teatro Clásico
            [
                {'event_id': 2, 'location': 'Platea Premium', 'price': 120.00, 'quantity_available': 100, 'quantity_sold': 0},
                {'event_id': 2, 'location': 'Platea', 'price': 75.00, 'quantity_available': 150, 'quantity_sold': 0},
                {'event_id': 2, 'location': 'Balcón', 'price': 40.00, 'quantity_available': 200, 'quantity_sold': 0}
            ],
            # Concierto Sinfónico
            [
                {'event_id': 3, 'location': 'Palco', 'price': 200.00, 'quantity_available': 30, 'quantity_sold': 0},
                {'event_id': 3, 'location': 'Platea', 'price': 90.00, 'quantity_available': 180, 'quantity_sold': 0},
                {'event_id': 3, 'location': 'Balcón', 'price': 50.00, 'quantity_available': 250, 'quantity_sold': 0}
            ],
            # Festival de Música Electrónica
            [
                {'event_id': 4, 'location': 'VIP', 'price': 180.00, 'quantity_available': 100, 'quantity_sold': 0},
                {'event_id': 4, 'location': 'General', 'price': 65.00, 'quantity_available': 500, 'quantity_sold': 0}
            ],
            # Conferencia de Tecnología
            [
                {'event_id': 5, 'location': 'Premium', 'price': 250.00, 'quantity_available': 50, 'quantity_sold': 0},
                {'event_id': 5, 'location': 'Estándar', 'price': 120.00, 'quantity_available': 200, 'quantity_sold': 0}
            ]
        ]
        
        # Create tickets
        for i, event_tickets in enumerate(tickets_data):
            for ticket_data in event_tickets:
                try:
                    ticket = db.execute_query('tickets', 'insert', ticket_data)
                    print(f"✅ Created ticket: {ticket_data['location']} for event {i+1}")
                except Exception as e:
                    print(f"❌ Error creating ticket: {e}")
        
        print(f"\n🎉 Successfully created {len(created_events)} events with tickets!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample events: {e}")
        return False

if __name__ == "__main__":
    create_sample_events()
