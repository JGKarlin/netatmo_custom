import logging
import aiohttp
import json
import aiofiles
from datetime import timedelta, datetime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

CONF_CLIENT_ID = 'client_id'
CONF_CLIENT_SECRET = 'client_secret'

# Define the path to the token file
TOKEN_FILE_PATH = '/config/netatmo_tokens.json'
SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    client_id = config.get(CONF_CLIENT_ID)
    client_secret = config.get(CONF_CLIENT_SECRET)

    if not client_id or not client_secret:
        _LOGGER.error("Missing client credentials")
        return False

    tokens = await load_tokens()
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    expires_at = tokens.get('expires_at')

    if not access_token or not refresh_token:
        _LOGGER.error("Missing tokens")
        return False

    if is_token_expired(expires_at):
        access_token, refresh_token, expires_at = await refresh_tokens(client_id, client_secret, refresh_token)
        if access_token and refresh_token and expires_at:
            await save_tokens(access_token, refresh_token, expires_at)
        else:
            _LOGGER.error("Failed to refresh tokens")
            return False

    async def async_update():
        _LOGGER.info("Updating Netatmo sensor data...")
        
        # Check if the token is expired
        tokens = await load_tokens()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_at = tokens.get('expires_at')
        
        if is_token_expired(expires_at):
            access_token, refresh_token, expires_at = await refresh_tokens(client_id, client_secret, refresh_token)
            if access_token and refresh_token and expires_at:
                await save_tokens(access_token, refresh_token, expires_at)
            else:
                _LOGGER.error("Failed to refresh tokens")
                return None
        
        data = await get_stations_data(access_token)
        if data:
            formatted_data = format_dashboard_data(data)
            if formatted_data:
                return formatted_data
            else:
                _LOGGER.error("Failed to format dashboard data")
        else:
            _LOGGER.error("Failed to fetch station data")
        return None

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Netatmo Custom Sensor",
        update_method=async_update,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_refresh()

    if coordinator.data:
        sensor = NetatmoSensor(coordinator)
        async_add_entities([sensor])
    else:
        _LOGGER.error("Failed to initialize Netatmo Custom Sensor")

class NetatmoSensor(Entity):
    def __init__(self, coordinator):
        self._coordinator = coordinator
        self._state = coordinator.data.get("Temperature")
        self._attributes = coordinator.data

    @property
    def name(self):
        return "Netatmo Custom Sensor"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        await self._coordinator.async_request_refresh()
        self._state = self._coordinator.data.get("Temperature")
        self._attributes = self._coordinator.data

async def load_tokens():
    try:
        async with aiofiles.open(TOKEN_FILE_PATH, 'r') as file:
            return json.loads(await file.read())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        _LOGGER.error(f"Error loading tokens: {e}")
        return {}

async def save_tokens(access_token, refresh_token, expires_at):
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at
    }
    try:
        async with aiofiles.open(TOKEN_FILE_PATH, 'w') as file:
            await file.write(json.dumps(tokens))
    except IOError as e:
        _LOGGER.error(f"Error saving tokens: {e}")

def is_token_expired(expires_at):
    return not expires_at or datetime.now() >= datetime.fromisoformat(expires_at)

async def refresh_tokens(client_id, client_secret, refresh_token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.netatmo.com/oauth2/token', data={
                'grant_type': 'refresh_token',
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token
            }) as response:
                if response.status == 200:
                    response_data = await response.json()
                    _LOGGER.info("Refreshed access token")
                    access_token = response_data['access_token']
                    refresh_token = response_data['refresh_token']
                    expires_at = (datetime.now() + timedelta(seconds=response_data['expires_in'])).isoformat()
                    return access_token, refresh_token, expires_at
                else:
                    _LOGGER.error(f"Error refreshing tokens - Status: {response.status}, Response: {await response.text()}")
                    return None, None, None
    except aiohttp.ClientError as e:
        _LOGGER.error(f"Error refreshing tokens: {e}")
        return None, None, None

async def get_stations_data(access_token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.netatmo.com/api/getstationsdata', params={
                'access_token': access_token
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.info("Obtained station data")
                    return data
                else:
                    _LOGGER.error(f"Error fetching station data - Status: {response.status}, Response: {await response.text()}")
                    return None
    except aiohttp.ClientError as e:
        _LOGGER.error(f"Error fetching station data: {e}")
        return None

def format_dashboard_data(data):
    try:
        dashboard_data = data['body']['devices'][0]['dashboard_data']
        formatted_data = {
            "Temperature": dashboard_data["Temperature"],
            "CO2": dashboard_data["CO2"],
            "Humidity": dashboard_data["Humidity"],
            "Noise": dashboard_data["Noise"],
            "Pressure": dashboard_data["Pressure"],
            "AbsolutePressure": dashboard_data["AbsolutePressure"],
            "TemperatureTrend": dashboard_data["temp_trend"],
            "PressureTrend": dashboard_data["pressure_trend"]
        }
        return formatted_data
    except (KeyError, IndexError) as e:
        _LOGGER.error(f"Error formatting dashboard data: {e}")
        return None
