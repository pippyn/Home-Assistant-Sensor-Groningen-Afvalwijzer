## Home Assisant sensor component for Groningen Afvalwijzer

Provides Home Assistant sensors for the Dutch waste collector Groningen Afvalwijzer using a scraper.

![alt text](https://github.com/pippyn/Home-Assisant-Sensor-Groningen-Afvalwijzer/blob/master/example.png)

### Install:
- Copy the groningen_afvalwijzer.py file to: [homeassistant]/config/custom_components/sensor/
- Add the content below to configuration.yaml:

```yaml
  sensor:
    - platform: groningen_afvalwijzer
      resources:                       # (at least 1 required)
        - restafval
        - papier
      postcode: 1111AA                 # (required)
      streetnumber: 1                  # (required)
```
Above example has 2 resources, but here is a complete list of available waste fractions:
- restafval
- papier
- gft
- kleding
- kerstboom
- chemokar
- kleinchemisch

## Custom updater
You can use the custom updater with this sensor
```yaml
custom_updater:
  track:
    - components
  component_urls:
    - https://raw.githubusercontent.com/pippyn/Home-Assisant-Sensor-Groningen-Afvalwijzer/master/custom_components.json
```
