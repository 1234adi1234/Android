# Location Tracker API

A Flask-based location tracking API with JSON storage and web interface, optimized for Render hosting.

## Features

- **RESTful API Endpoints**:
  - `POST /update` - Add new location (accepts JSON with name, lat, lon, timestamp)
  - `GET /get` - Get the latest saved location
  - `GET /all` - Get all stored locations as JSON array
  
- **Web Interface**:
  - Clean, responsive web form for manual location entry
  - Real-time location detection using browser geolocation API
  - Interactive table displaying all saved locations
  - Direct links to Google Maps for each location
  - Bootstrap-themed dark UI

- **Data Storage**:
  - JSON file-based storage (`locations.json`)
  - Automatic data validation and error handling
  - Persistent storage across deployments

## API Endpoints

### POST /update
Add a new location to the tracker.

**Request Body (JSON):**
```json
{
  "name": "My Location",
  "lat": 40.7128,
  "lon": -74.0060
}
