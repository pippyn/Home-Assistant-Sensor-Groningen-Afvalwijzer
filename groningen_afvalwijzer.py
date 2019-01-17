"""
Sensor component for Groningen Afvalwijzer
Original Author:  Pippijn Stortelder
Current Version:  1.0.3  20190117 - Pippijn Stortelder
20190108 - Initial Release
20190109 - Code clean up - fixed error handling
20190114 - Github release
20190117 - FIXED small bug with empty date

Description:
  Provides sensors for the Dutch waste collector Groningen Afvalwijzer.

Save the file as groningen_afvalwijzer.py in [homeassistant]/config/custom_components/sensor/

resources options:
- restafval
- papier
- gft
- kleding
- kerstboom
- chemokar
- kleinchemisch

Example config:
Configuration.yaml:
  sensor:
    - platform: groningen_afvalwijzer
      resources:                       (at least 1 required)
        - restafval
        - papier
      postcode: 1111AA                 (required)
      streetnumber: 1                  (required)
"""

import logging
from datetime import datetime
from datetime import timedelta
import voluptuous as vol
import urllib.request
import urllib.error
from html_table_parser import HTMLTableParser

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_RESOURCES)
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

__version__ = '1.0.3'

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=1)
CONF_POSTCODE = 'postcode'
CONF_STREETNUMBER = 'streetnumber'
SENSOR_PREFIX = 'Afvalwijzer '
ATTR_LAST_UPDATE = 'Last update'
ATTR_HIDDEN = 'Hidden'

SENSOR_TYPES = {
    'restafval': ['Grijze container', '', 'mdi:recycle'],
    'papier': ['Oud papier', '', 'mdi:recycle'],
    'gft': ['Groene container', '', 'mdi:recycle'],
    'kleding': ['Kleding, textiel en schoenen', '', 'mdi:recycle'],
    'kerstboom': ['Kerstboom', '', 'mdi:recycle'],
    'chemokar': ['Standplaats Chemokar', '', 'mdi:recycle'],
    'kleinchemisch': ['Klein chemisch afval', '', 'mdi:recycle'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Required(CONF_POSTCODE, default='1111AA'): cv.string,
    vol.Required(CONF_STREETNUMBER, default='1'): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug('Setup Groningen Afvalwijzer retriever')

    postcode = config.get(CONF_POSTCODE)
    street_number = config.get(CONF_STREETNUMBER)

    try:
        data = AfvalwijzerData(postcode, street_number)
    except urllib.error.HTTPError as error:
        _LOGGER.error(error.reason)
        return False

    entities = []

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [sensor_type.title(), '', 'mdi:recycle']

        entities.append(AfvalwijzerSensor(data, sensor_type))

    add_entities(entities)


class AfvalwijzerData(object):

    def __init__(self, postcode, streetnumber):
        self.data = None
        self.postcode = postcode
        self.street_number = streetnumber

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        _LOGGER.debug('Updating Waste collection dates using scraper')

        try:
            today = datetime.today()
            year = today.strftime('%Y')
            suffix_url = self.postcode + "/" + self.street_number + "/" + year + "/"
            url = "https://gemeente.groningen.nl/afvalwijzer/groningen/" + suffix_url
            req = urllib.request.Request(url=url)
            f = urllib.request.urlopen(req)
            xhtml = f.read().decode('utf-8')
            p = HTMLTableParser()
            p.feed(xhtml)
            waste_dict = {}
            fraction_name = ""
            if p.tables[0]:
                for table_row in p.tables[0][1:]:
                    for i in range(13):
                        if table_row[i]:
                            if i == 0:
                                fraction_name = table_row[i].split("  ")[0]
                                if "Klein chemisch afval kunt u" in fraction_name:
                                    fraction_name = "Klein chemisch afval"
                                waste_dict[fraction_name] = []
                            else:
                                for day in table_row[i].split(" "):
                                    try:
                                        waste_dict[fraction_name].append(
                                            datetime.strptime(
                                                (day.replace("*", "") + " " + str(i) + " " + year), "%d %m %Y"))
                                    except (ValueError, TypeError):
                                        pass
                self.data = waste_dict
            else:
                _LOGGER.error('Error occurred while fetching data. Probably the postcode/street number is incorrect.')
                self.data = None
        except urllib.error.URLError as exc:
            _LOGGER.error('Error occurred while fetching data: %r', exc.reason)
            self.data = None
            return False


class AfvalwijzerSensor(Entity):

    def __init__(self, data, sensor_type):
        self.data = data
        self.type = SENSOR_TYPES[sensor_type][0]
        self._name = SENSOR_PREFIX + SENSOR_TYPES[sensor_type][0]
        self._unit = SENSOR_TYPES[sensor_type][1]
        self._icon = SENSOR_TYPES[sensor_type][2]
        self._hidden = False
        self._state = None
        self._last_update = None

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return {
            ATTR_LAST_UPDATE: self._last_update,
            ATTR_HIDDEN: self._hidden
        }

    @property
    def unit_of_measurement(self):
        return self._unit

    def update(self):
        self.data.update()
        waste_data = self.data.data
        try:
            if waste_data:
                if self.type in waste_data:
                    today = datetime.today()
                    collection_date = self.get_next_collection(today, waste_data, self.type)
                    if collection_date:
                        self._last_update = today.strftime('%d-%m-%Y %H:%M')
                        date_diff = (collection_date - today).days + 1
                        if date_diff >= 8:
                            self._state = collection_date.strftime('%d-%m-%Y')
                        elif date_diff > 1:
                            self._state = collection_date.strftime('%A, %d-%m-%Y')
                        elif date_diff == 1:
                            self._state = collection_date.strftime('Tomorrow, %d-%m-%Y')
                        elif date_diff <= 0:
                            self._state = collection_date.strftime('Today, %d-%m-%Y')
                        else:
                            self._state = None
                    else:
                        self._state = None
                else:
                    self._state = None
                    self._hidden = True
        except ValueError:
            self._state = None
            self._hidden = True

    @staticmethod
    def get_next_collection(today, waste_dict, fraction):
        next_collection_date = today
        for collection_date in waste_dict[fraction]:
            if collection_date > today:
                next_collection_date = collection_date
                break
        if next_collection_date == today:
            next_collection_date = None
        return next_collection_date
