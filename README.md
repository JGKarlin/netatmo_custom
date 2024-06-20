# Netatmo Sensor Integration for Home Assistant

This custom component integrates Netatmo weather station data into Home Assistant. It periodically fetches sensor data from the Netatmo API, ensuring tokens are managed and refreshed automatically. I created this custom integration because the official Netatmo integration now built-in to Home Assistant is not reliable and not consistently maintained.

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
3.	Token File:
Create an empty JSON file named netatmo_tokens.json in the /config/ directory of your Home Assistant setup. This file will store the tokens.

Usage

	1.	Restart Home Assistant:
After adding the configuration and placing the script, restart Home Assistant to load the new integration.
	2.	Check Logs:
Monitor the Home Assistant logs to ensure the integration is working correctly. Look for messages related to Netatmo sensor updates and token handling.
	3.	View Sensor Data:
Once the integration is running, the Netatmo sensor data will be available in Home Assistant. You can create automations, display data in the dashboard, and use it in other Home Assistant functionalities.

Detailed Script Functionality

Imports and Constants

	•	Imports: The script imports necessary modules such as logging, aiohttp, json, aiofiles, and datetime.
	•	Constants: Defines configuration parameters (CONF_CLIENT_ID, CONF_CLIENT_SECRET), the path to the token file, and the scan interval.

Setup Platform

	•	Function: async_setup_platform
	•	Description: Initializes the integration by retrieving the client ID and secret from the configuration, loading tokens, and validating them.

Token Management

	•	Functions: load_tokens, save_tokens, is_token_expired, refresh_tokens
	•	Description: Handles token storage, validation, and refreshing using the Netatmo API.

Data Update

	•	Function: async_update
	•	Description: Periodically updates the sensor data by fetching it from the Netatmo API, ensuring tokens are valid before making the request.

Fetching Data

	•	Function: get_stations_data
	•	Description: Makes an HTTP GET request to the Netatmo API to retrieve weather station data and processes it.

Formatting Data

	•	Function: format_dashboard_data
	•	Description: Extracts and formats relevant information from the API response for use in Home Assistant.

Logging

The script uses Python’s built-in logging module to log information, errors, and debug messages. This can help in monitoring the integration’s performance and troubleshooting issues.

License

This project is licensed under the MIT License. See the LICENSE file for details.
