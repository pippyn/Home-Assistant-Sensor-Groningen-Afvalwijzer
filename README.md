## Home Assisant sensor component for Groningen Afvalwijzer

Provides Home Assistant sensors for the Dutch waste collector Groningen Afvalwijzer using a scraper.

![alt text](https://github.com/pippyn/Home-Assisant-Sensor-Groningen-Afvalwijzer/blob/master/example.png)

### Install:
- Copy the files in the /custom_components/groningen_afvalwijzer/ folder to: [homeassistant]/config/custom_components/groningen_afvalwijzer/

Example config:
```yaml
  sensor:
    - platform: groningen_afvalwijzer
      resources:                       # (at least 1 required)
        - restafval
        - papier
      postcode: 1111AA                 # (required)
      streetnumber: 1                  # (required)
      dateformat: '%d-%m'              # (optional)
      dateonly: 1                      # (optional)
```
Above example has 2 resources, but here is a complete list of available waste fractions:
- restafval
- papier
- gft
- kleding
- kerstboom
- chemokar
- kleinchemisch

### Date format
```yaml
dateformat:
```
If you want to adjust the way the date is presented. You can do it using the dateformat option. All [python strftime options](http://strftime.org/) should work.
Default is '%d-%m-%Y', which will result in per example: 
```yaml
21-9-2019.
```
If you wish to remove the year and the dashes and want to show the name of the month abbreviated, you would provide '%d %b'. Which will result in: 
```yaml
21 Sep
```

### Date only
```yaml
dateonly: 1
```
If you don't want to add dayname, tomorrow or today in front of date activate this option. Default is 0.

## Custom updater
You can use the custom updater with this sensor

Home assistant 88 and higher:
```yaml
custom_updater:
  track:
    - components
  component_urls:
    - https://raw.githubusercontent.com/pippyn/Home-Assistant-Sensor-Groningen-Afvalwijzer/master/custom_components.json
```
Before Home assistant 88:
```yaml
custom_updater:
  track:
    - components
  component_urls:
    - https://raw.githubusercontent.com/pippyn/Home-Assistant-Sensor-Groningen-Afvalwijzer/master/custom_components_old.json
```
