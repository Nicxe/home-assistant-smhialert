import logging
import async_timeout
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity import DeviceEntryType  # Importera DeviceEntryType
from .const import (
    DOMAIN,
    CONF_DISTRICT,
    CONF_LANGUAGE,
    DEFAULT_NAME,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = SmhiAlertCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        _LOGGER.error("Failed to fetch initial data: %s", ex)
        return False  # Indikerar att setup misslyckades

    async_add_entities([SMHIAlertSensor(coordinator, entry)], True)
    return True

class SMHIAlertSensor(SensorEntity):
    """Representation of the SMHI Alert sensor."""

    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self.entry = entry  # Spara config_entry för senare användning
        self._name = DEFAULT_NAME
        self._icon = "mdi:alert"

    @property
    def unique_id(self):
        """Return a unique ID to identify this sensor."""
        return f"{self.entry.entry_id}_smhi_alert_sensor"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the sensor icon."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get('state')

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self.coordinator.data.get('attributes')

    @property
    def available(self):
        """Return True if sensor is available."""
        return self.coordinator.last_update_success

    @property
    def should_poll(self):
        """No need to poll, coordinator notifies entity of updates."""
        return False

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": "SMHI Alert",
            "manufacturer": "SMHI",
            "entry_type": DeviceEntryType.SERVICE,  # Använd DeviceEntryType istället för sträng
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

class SmhiAlertCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from SMHI."""

    def __init__(self, hass, entry):
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.district = entry.data.get(CONF_DISTRICT)
        self.language = entry.data.get(CONF_LANGUAGE)
        self.session = aiohttp_client.async_get_clientsession(hass)
        self.available = True

        super().__init__(
            hass,
            _LOGGER,
            name="SMHI Alert",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from SMHI."""
        url = 'https://opendata-download-warnings.smhi.se/ibww/api/version/1/warning.json'

        data = {
            'state': "No Alerts" if self.language == 'en' else "Inga varningar",
            'attributes': {
                "messages": [],
                "notice": ""
            }
        }

        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: {response.status}")
                    json_data = await response.json()

            messages, notice = self._process_data(json_data)

            if messages:
                data['state'] = "Alert" if self.language == 'en' else "Varning"
                data['attributes']['messages'] = messages
                data['attributes']['notice'] = notice

            self.available = True
            return data

        except Exception as e:
            self.available = False
            raise UpdateFailed(f"Error updating data: {e}") from e

    def _process_data(self, data):
        """Process the data received from SMHI."""
        messages = []
        notice = ""

        if not data:
            return messages, notice

        for alert in data:
            event = alert.get('event', {}).get(self.language, '')
            warning_areas = alert.get('warningAreas', [])
            for area in warning_areas:
                affected_areas = area.get('affectedAreas', [])
                valid_areas = []

                for affected_area in affected_areas:
                    area_id = str(affected_area.get('id'))
                    area_name = affected_area.get(self.language)
                    if area_id == self.district or self.district == 'all':
                        valid_areas.append(area_name)

                if not valid_areas:
                    continue

                severity_info = area.get('warningLevel', {})
                code = severity_info.get('code', '').upper()
                severity = severity_info.get(self.language, '')
                level = severity

                descr = area.get('eventDescription', {}).get(self.language, '')
                start_time = area.get('approximateStart', '')
                end_time = area.get('approximateEnd', '')
                published = area.get('published', '')

                # Details
                details = ""
                descriptions = area.get('descriptions', [])
                for desc in descriptions:
                    title = desc.get('title', {}).get(self.language, '')
                    text = desc.get('text', {}).get(self.language, '')
                    details += f"{title}: {text}\n"

                msg = {
                    "event": event,
                    "start": start_time,
                    "end": end_time or ('Unknown' if self.language == 'en' else 'Okänt'),
                    "published": published,
                    "code": code,
                    "severity": severity,
                    "level": level,
                    "descr": descr,
                    "details": details,
                    "area": ", ".join(valid_areas),
                    "event_color": self._get_event_color(code)
                }

                messages.append(msg)
                notice += self._format_notice(msg)

        return messages, notice

    def _get_event_color(self, code):
        """Return color code based on severity code."""
        code_map = {
            "RED": "#FF0000",
            "ORANGE": "#FF7F00",
            "YELLOW": "#FFFF00"
        }
        return code_map.get(code, "#FFFFFF")

    def _format_notice(self, msg):
        """Format the notice string."""
        if self.language == 'en':
            return f"""[{msg["severity"]}] ({msg["published"]})
District: {msg["area"]}
Level: {msg["level"]}
Type: {msg["event"]}
Start: {msg["start"]}
End: {msg["end"]}
{msg["details"]}\n"""
        else:
            return f"""[{msg["severity"]}] ({msg["published"]})
Område: {msg["area"]}
Nivå: {msg["level"]}
Typ: {msg["event"]}
Start: {msg["start"]}
Slut: {msg["end"]}
Beskrivning:
{msg["details"]}\n"""
