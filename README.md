# Netatmo Sensor Integration for Home Assistant

This custom component integrates Netatmo weather station data into Home Assistant. It periodically fetches sensor data from the Netatmo API, ensuring tokens are managed and refreshed automatically.

## Features

- Retrieves real-time data from Netatmo weather stations.
- Automatically handles token refresh and storage.
- Provides formatted weather data for Home Assistant sensors.

## Installation

### Prerequisites

1. Home Assistant must be installed and configured.
2. Ensure you have a Netatmo weather station and have registered an application to obtain the client ID and secret.

### Steps

1. **Copy the Script**:

   Save the `sensor.py` script to your Home Assistant custom components directory, typically located at `/config/custom_components/netatmo/`.

2. **Configuration**:

   In your Home Assistant configuration file (`configuration.yaml`), add the Netatmo sensor configuration:

   ```yaml
   sensor:
     - platform: netatmo
       client_id: YOUR_CLIENT_ID
       client_secret: YOUR_CLIENT_SECRET
