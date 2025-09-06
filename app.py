import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

LOCATIONS_FILE = "locations.json"

def load_locations():
    """Load locations from JSON file"""
    try:
        if os.path.exists(LOCATIONS_FILE):
            with open(LOCATIONS_FILE, 'r') as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading locations: {e}")
        return []

def save_locations(locations):
    """Save locations to JSON file"""
    try:
        with open(LOCATIONS_FILE, 'w') as f:
            json.dump(locations, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving locations: {e}")
        return False

def validate_location_data(data):
    """Validate location data"""
    required_fields = ['name', 'lat', 'lon']
    
    if not isinstance(data, dict):
        return False, "Invalid data format"
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    try:
        lat = float(data['lat'])
        lon = float(data['lon'])
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        
        if not (-180 <= lon <= 180):
            return False, "Longitude must be between -180 and 180"
            
    except (ValueError, TypeError):
        return False, "Latitude and longitude must be valid numbers"
    
    if not data['name'].strip():
        return False, "Name cannot be empty"
    
    return True, "Valid"

@app.route('/')
def index():
    """Main page with form and location table"""
    locations = load_locations()
    return render_template('index.html', locations=locations)

@app.route('/update', methods=['POST'])
def update_location():
    """API endpoint to add new location"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                'name': request.form.get('name', '').strip(),
                'lat': request.form.get('lat', '').strip(),
                'lon': request.form.get('lon', '').strip()
            }
        
        # Validate the data
        is_valid, message = validate_location_data(data)
        if not is_valid:
            if request.is_json:
                return jsonify({'error': message}), 400
            else:
                flash(f'Error: {message}', 'error')
                return redirect(url_for('index'))
        
        # Load existing locations
        locations = load_locations()
        
        # Add timestamp and create new location entry
        new_location = {
            'name': data['name'].strip(),
            'lat': float(data['lat']),
            'lon': float(data['lon']),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to locations list
        locations.append(new_location)
        
        # Save to file
        if save_locations(locations):
            if request.is_json:
                return jsonify({'message': 'Location saved successfully', 'location': new_location}), 201
            else:
                flash('Location saved successfully!', 'success')
                return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'error': 'Failed to save location'}), 500
            else:
                flash('Error: Failed to save location', 'error')
                return redirect(url_for('index'))
            
    except Exception as e:
        print(f"Error in update_location: {e}")
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        else:
            flash('Error: Internal server error', 'error')
            return redirect(url_for('index'))

@app.route('/get', methods=['GET'])
def get_latest_location():
    """API endpoint to get the latest location"""
    try:
        locations = load_locations()
        
        if not locations:
            return jsonify({'message': 'No locations found'}), 404
        
        # Return the most recent location (last in the list)
        latest_location = locations[-1]
        return jsonify(latest_location), 200
        
    except Exception as e:
        print(f"Error in get_latest_location: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/all', methods=['GET'])
def get_all_locations():
    """API endpoint to get all locations"""
    try:
        locations = load_locations()
        return jsonify(locations), 200
        
    except Exception as e:
        print(f"Error in get_all_locations: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/clear', methods=['POST'])
def clear_locations():
    """Clear all locations (for web interface)"""
    try:
        if save_locations([]):
            flash('All locations cleared successfully!', 'success')
        else:
            flash('Error: Failed to clear locations', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error in clear_locations: {e}")
        flash('Error: Internal server error', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Create empty locations file if it doesn't exist
    if not os.path.exists(LOCATIONS_FILE):
        save_locations([])
    
    # Get port from environment variable for Render deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
