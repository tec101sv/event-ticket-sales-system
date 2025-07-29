#!/usr/bin/env python3
"""
Script to test Supabase connection and check if we have events
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_db
from config import Config

def test_connection():
    """Test Supabase connection"""
    print("Testing Supabase connection...")
    print(f"Supabase URL: {Config.SUPABASE_URL}")
    
    try:
        db = get_db()
        client = db.get_client()
        
        print("✅ Supabase connection successful!")
        
        # Check users table
        try:
            users = db.execute_query('users')
            print(f"Users in database: {len(users)}")
        except Exception as e:
            print(f"Error checking users: {e}")
        
        # Check event_types
        try:
            event_types = db.execute_query('event_types')
            print(f"Event types: {len(event_types)}")
            for et in event_types[:3]:
                print(f"  - {et['name']}")
        except Exception as e:
            print(f"Error checking event_types: {e}")
        
        # Check venues
        try:
            venues = db.execute_query('venues')
            print(f"Venues: {len(venues)}")
            for venue in venues[:3]:
                print(f"  - {venue['name']}")
        except Exception as e:
            print(f"Error checking venues: {e}")
        
        # Check artists
        try:
            artists = db.execute_query('artists')
            print(f"Artists: {len(artists)}")
            for artist in artists[:3]:
                print(f"  - {artist['name']}")
        except Exception as e:
            print(f"Error checking artists: {e}")
        
        # Check events
        try:
            events = db.execute_query('events')
            print(f"Events in database: {len(events)}")
            
            if len(events) > 0:
                print("\nSample events:")
                for event in events[:3]:
                    print(f"  - {event['title']} on {event['event_date']}")
            else:
                print("No events found - we need to create some!")
                
        except Exception as e:
            print(f"Error checking events: {e}")
        
        return True
            
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
