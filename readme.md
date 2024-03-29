# JaMa Villa Home Assistant Configuration

![Project Maintenance][maintenance-shield]
[![Home Assistant][home-assistant-shield]](home-assistant)
![esphome.io][esphome-shield]

[![License][license-shield]](LICENSE)

[![Circle CI][circleci-shield]][circleci]
[![GitHub Activity][commits-shield]][commits]
[![GitHub Last Commit][last-commit-shield]][commits]

[![Twitter][twitter-badge]][twitter]

Here's our JaMa Villa Home Assistant configuration, running our home
automation. [Home Assistant][home-assistant] (HA) is an open-source home
automation platform which allows you to control devices easily, track multiple
sensors and integrate with a wide variety of commercial & DIY solutions.
I currently run it via [Hass.io](https://www.home-assistant.io/hassio/) on
a single ODROID-N2. My HA configuration structure is heavily inspired by
the work done by [Franck Nijhof](https://github.com/frenck)

![HA](img/header.png "header")

I try regularly update my configuration files, there is always something to
tweak or improve 😉. This repository is to inspire others, be free to use the
code from this repo for your own HA setup. If you think it is helpful and like
anything here, Be sure to 🌟 the GitHub repo.

## System Overview

![Setup](img/setup.png "setup")

## House Automation Hardware

### Host System

My Home Assistant system currently runs on a ODROID-N2. All is managed by hass.io and the following add-ons are currently used:

- [AdGuard Home](https://github.com/hassio-addons/addon-adguard-home)
- [ESPHome](https://esphome.io/)
- [Grafana](https://github.com/hassio-addons/addon-grafana)
- [InfluxDB](https://github.com/hassio-addons/addon-influxdb)
- [Log Viewer](https://github.com/hassio-addons/addon-log-viewer)
- [Mosquitto MQTT broker](https://home-assistant.io/addons/mosquitto/)
- [SSH & Web Terminal](https://github.com/hassio-addons/addon-ssh)
- [Samba share](https://home-assistant.io/addons/samba/)
- [Visual Studio Code](https://github.com/hassio-addons/addon-vscode)

#### Hubs

| Device                                                                                                                                                               |                                                      Home Assistant                                                       | Notes                                                                                          |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------:|------------------------------------------------------------------------------------------------|
| [Homematic CCU3](https://www.homematic-ip.com/en/products/detail/smart-home-central-control-unit-ccu3.html)                                                          |                             [Homematic](https://www.home-assistant.io/components/homematic/)                              | Used to control all Homematic devices                                                          |
| [deCONZ Conbee II](https://www.phoscon.de/en/conbee2)                                                                                                                |                                [deCONZ](https://www.home-assistant.io/components/deconz/)                                 | The main ZigBee Hub                                                                            |
| [Arlo Hub](https://shop.arlo.com/accessories.arlo/VMB4000-100NAS.html)                                                                                               |                             [Aarlo](https://github.com/twrecked/hass-aarlo) custom component                              | Arlo camera system integration                                                                 |

#### Network

| Device                                                                                                                                               |                  Quantity                  | Home Assistant                                                                                     | Notes                                                                                    |
|------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| [Ubiquiti Networks UniFi Switch - 16 Ports (US-16-150W)](https://www.ui.com/unifi-switching/unifi-switch-16-150w/)                                   |                     1                      | [Ubiquiti Unifi](https://www.home-assistant.io/components/unifi/)                                  | Primary network switch                                                                   |
| [Ubiquiti Networks USW Flex Mini Swicth (USW-Flex-Mini)](https://store.ui.com/products/usw-flex-mini)                                                |                     1                      | [Ubiquiti Unifi](https://www.home-assistant.io/components/unifi/)                                  | Office desk mini switch                                                                  |
| [Ubiquiti Networks Unifi AP Lite (UAP-AC-LITE)](https://www.ui.com/unifi/unifi-ap-ac-lite/)                                                          |                     2                      | [Ubiquiti Unifi](https://www.home-assistant.io/components/unifi/)                                  | Wireless Access Point for interior use.                                                  |
| [Ubiquiti Unifi Security Gateway (USG)](https://www.ui.com/unifi-routing/usg/)                                                                       |                     1                      | [Ubiquiti Unifi](https://www.home-assistant.io/components/unifi/)                                  | Main router & firewall device                                                            |
| [Draytek Vigor 130 ADSL/VDSL modem](https://www.draytek.com/products/vigor130/)                                                                      |                     1                      | n/a                                                                                                | Main DSL device fot the connection to the outside world                                  |

On network gear we are all-in for Unifi devices, they provide a reliable and stable network for our house. Many of the devices have been in service for years. The Draytek modem is connected to the DSL line of the internet provider. The Unifi network equipment is also used as one of the presence detection methods.

#### Lighting

| Device                                                                                                                                                                       |               Quantity               |                                           Home Assistant                                            | Notes                                                                 |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------:|:---------------------------------------------------------------------------------------------------:|-----------------------------------------------------------------------|
| [Philips Hue White and Color Ambiance](https://www2.meethue.com/en-gb/p/hue-white-and-colour-ambience-1-pack-e27/8718699673109)                                              |                  3                   |              [Philips Hue Light](https://www.home-assistant.io/components/light.hue/)               | Color-changing smart bulbs                                            |
| [Philips Hue White and Color Ambiance LightStrip](https://www2.meethue.com/en-gb/p/hue-white-and-colour-ambience-lightstrip-plus/7190155PH)                                  |                  2                   |              [Philips Hue Light](https://www.home-assistant.io/components/light.hue/)               | Ambiante lights in kitchen and for TV wall                            |
| [Paulman RGBW Controller ZigBee](https://de.paulmann.com/innenleuchten/smart-home/zigbee/smarthome-zigbee-maxled-rgbw-controller-max.-72w/50047)                             |                  1                   |               [deCONZ Light](https://www.home-assistant.io/components/deconz/#light)                | Driver for old reused classic LED strip                               |
| [Sonoff S20 Smart Socket](https://sonoff.tech/product/wifi-smart-plugs/s20)                                                                                                  |                  11                  |                                                                                                     | The main Christmas season light driver                                |
| ESP8266 with [WLED](https://kno.wled.ge/)                                                                                                                                    |                  3                   |                      [WLED](https://www.home-assistant.io/integrations/wled/)                       | Controlling outdoor fairy lights                                      |

#### Outlets & Switches

| Device                                                                                                                                                                                                                |    Quantity    |                                Home Assistant                                 | Notes                                                                    |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------:|:-----------------------------------------------------------------------------:|--------------------------------------------------------------------------|
| [Wireless Switch Actuator 1-channel with power metering (HM-ES-PMSw1-Pl-DN-R1)](https://www.eq-3.com/products/homematic/detail/wireless-switch-actuator-1-channel-with-power-metering-plug-adapter-type-f.html)       |       3        |    [Homematic Switch](https://www.home-assistant.io/components/homematic/)    | Indoor outlet for selected devices, mainly for power metering            |
| [Wireless Switch Actuator 1-channel, flush-mount (HM-LC-Sw1-FM)](https://www.eq-3.com/products/homematic/detail/homematic-wireless-switch-actuator-1-channel-flush-mount.html)                                        |       1        |    [Homematic Switch](https://www.home-assistant.io/components/homematic/)    | Hallway light switch                                                     |
| [Wireless Switch Actuator 1-channel, DIN-rail mount (HM-LC-Sw1-DR)](https://www.eq-3.com/products/homematic/detail/wireless-switch-actuator-1-channel-din-rail-mount.html)                                            |       2        |    [Homematic Switch](https://www.home-assistant.io/components/homematic/)    | Used to control outdoor                                                  |
| [Wireless Switch Actuator 2-channel with power metering, DIN-rail mount (HM-ES-PMSw1-DR)](https://de.elv.com/elv-homematic-hutschienen-schaltaktor-mit-leistungsmessung-hm-es-pmsw1-dr-150749?fs=648590641)           |       3        |    [Homematic Switch](https://www.home-assistant.io/components/homematic/)    | Used to control pumps of the pool and water tank                         |
| [Sonoff S20 Smart Socket](https://sonoff.tech/product/wifi-smart-plugs/s20)                                                                                                                                           |       11       |        [Tasmota](https://www.home-assistant.io/integrations/tasmota/)         | The main Christmas season light driver                                   |
| [Sonoff 4CH Pro R2](https://sonoff.tech/product/wifi-diy-smart-switches/4ch-r2-pro-r2)                                                                                                                                |       1        |        [Tasmota](https://www.home-assistant.io/integrations/tasmota/)         | Used to control outdoor garden low power lighting                        |
| [Sonoff TH16](https://sonoff.tech/product/wifi-diy-smart-switches/th10-th16)                                                                                                                                          |       1        |        [Tasmota](https://www.home-assistant.io/integrations/tasmota/)         | Carport light and outdoor temperature & humidity with Si7021 sensor      |
| [Shelly 2.5](https://shelly.cloud/products/shelly-25-smart-home-automation-relay/)                                                                                                                                    |       3        |         [Shelly](https://www.home-assistant.io/integrations/shelly/)          | Used to control various outdoor, pond pumps and pool lighting            |

Switches and outlets are used in various capacities, most are for lighting and some are for pool & pump devices. For devices consuming more energy I prefer the Homematic devices, they give a good and secure overall impression. For seasonal Christmas lighting (most are low power LEDs) I mainly use Sonoff outlets flashed with [Tasmota Firmware](https://github.com/arendst/Tasmota).

#### Sensors

| Device                                                                                                                                                          | Quantity |                              Home Assistant                              | Notes                                                                                                                                     |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|:------------------------------------------------------------------------:|-------------------------------------------------------------------------------------------------------------------------------------------|
| [Wireless Differential Temperature Sensor (HM-WDS30-OT2-SM)](https://www.eq-3.com/products/homematic/detail/homematic-wireless-temperature-sensor-outdoor.html) |    2     | [Homematic Sensor](https://www.home-assistant.io/components/homematic/)  | Pool & solar temperature sensor for pool automation                                                                                       |
| [Xiaomi Aqara Smart Temperature Humidity Sensor](https://nis-store.com/sockets-and-sensors/aqara-temperature-and-humidity-sensor/)                              |    6     | [deCONZ Sensor](https://www.home-assistant.io/components/deconz/#sensor) | Main indoor temperature & humidity sensor                                                                                                 |
| [Xiaomi Aqara Smart Vibration Sensor](https://www.gearbest.com/smart-home-controls/pp_009661787808.html)                                                        |    2     | [deCONZ Sensor](https://www.home-assistant.io/components/deconz/#sensor) | Moving detection of our garden bench ;-)                                                                                                  |
| [Sonoff TH16](https://sonoff.tech/product/wifi-diy-smart-switches/th10-th16) with Si7021 sensor                                                                 |    1     |  [MQTT Sensor](https://www.home-assistant.io/integrations/sensor.mqtt/)  | Garden & outdoor temperature & humidity sensor                                                                                            |
| [luftdaten.info](https://luftdaten.info/) air quality sensor                                                                                                    |    1     |     [REST Sensor](https://www.home-assistant.io/integrations/rest/)      | DYI Fine dust & air quality sensor based on SDS011 board with additional BME280 sensor to measure temperature & air pressure and humidity |

Most of the sensor got replaced with Xiaomi Aqara devices recently, they are small and very reliable, connected via ZigBee deCONZ. Unfortunately, they are only for indoor use, so I keep the Homematic HM-WDS30-OT2-SM for outdoor.

#### Security

| Device                                                                                                                                                                 |         Quantity         |                                         Home Assistant                                         | Notes                                                                                        |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------:|:----------------------------------------------------------------------------------------------:|----------------------------------------------------------------------------------------------|
| [Wireless Door/Window Sensor, optical (HM-Sec-SCo)](https://www.eq-3.com/products/homematic/detail/homematic-wireless-door-window-sensor-optical.html)                 |            9             |         [Homematic Binary Sensor](https://www.home-assistant.io/components/homematic/)         | Door sensors to detect if windows & exterior doors have been opened / closed                 |
| [Wireless Shutter Contact (HM-Sec-SC-2)](https://www.eq-3.com/products/homematic/detail/homematic-wireless-window-sensor.html)                                         |            1             |         [Homematic Binary Sensor](https://www.home-assistant.io/components/homematic/)         | Door sensors to detect if windows have been opened / closed                                  |
| [Wireless Motion Detector (HM-Sec-MDIR-3)](https://www.eq-3.com/products/homematic/detail/homematic-wireless-motion-detector-indoor.html)                              |            3             |         [Homematic Binary Sensor](https://www.home-assistant.io/components/homematic/)         | Indoor motion detection                                                                      |
| [Wireless Siren (HM-Sec-Sir-WM)](https://www.eq-3.com/products/homematic/detail/homematic-wireless-siren-with-signal-light.html)                                       |            2             |            [Homematic Switch](https://www.home-assistant.io/components/homematic/)             | Indoor alarm siren                                                                           |
| [Rademacher DuoFern Motor Actuator 9471-1](https://www.rademacher.de/en/smart-home/produkte/rohrmotor-aktor-9471-1?productID=35140662)                                 |            9             |               [pyduofern](https://github.com/gluap/pyduofern) (custom component)               | Flush-mounted actuator for roller shutter motors                                             |

#### Media & Voice Assistant

| Device                                                                                          |                 Quantity                  |                                             Home Assistant                                             | Notes                                                                                                                                      |
|-------------------------------------------------------------------------------------------------|:-----------------------------------------:|:------------------------------------------------------------------------------------------------------:|--------------------------------------------------------------------------------------------------------------------------------------------|
| [Sonos Move](https://www.sonos.com/en-us/shop/move.html)                                        |                     1                     |                 [Sonos](https://www.home-assistant.io/components/media_player.sonos/)                  | This little thing has enough power to stream music into our livingroom and we take it outside very often.                                  |
| [Sonos Roam](https://www.sonos.com/en-us/shop/move.html)                                        |                     1                     |                 [Sonos](https://www.home-assistant.io/components/media_player.sonos/)                  | Some music for my office                                                                                                                   |
| [Sonos PlayBar](https://www.sonos.com/en-us/shop/playbar.html)                                  |                     1                     |                 [Sonos](https://www.home-assistant.io/components/media_player.sonos/)                  | TV and livingroom sound                                                                                                                    |
| [Sonos Sub](https://www.sonos.com/en-us/shop/sub.html)                                          |                     1                     |                 [Sonos](https://www.home-assistant.io/components/media_player.sonos/)                  | TV and livingroom sound                                                                                                                    |
| [Amazon Echo](https://amzn.to/2HM0XIW)                                                          |                     1                     |                         Via [Nabu Casa](https://www.home-assistant.io/cloud/)                          | Voice control                                                                                                                              |

#### Cameras

| Device                                                                                        |                              Quantity                              |                                              Home Assistant                                               | Notes                                                                                                            |
|-----------------------------------------------------------------------------------------------|:------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------------:|------------------------------------------------------------------------------------------------------------------|
| [Arlo HD](https://www.arlo.com/)                                                              |                                 3                                  |                              [Aarlo](https://github.com/twrecked/hass-aarlo)                              | Started with these, then added Arlo Pro 2 later                                                                  |
| [Arlo Pro 2](https://www.arlo.com/)                                                           |                                 2                                  |                              [Aarlo](https://github.com/twrecked/hass-aarlo)                              | Definitely much better quality then the 1st generation                                                           |

The main argument for us to choose Arlo cameras were they are powered
via a battery since we have them placed mainly in places without power supply.
They only record if motion (or sound on the Arlo Pro 2) is detected.
The original Arlo HD requires special batteries and last ~6 months on one set.
The Arlo Pro 2 comes with a rechargeable battery pack or can be operated
with USB power supply.

#### Car

| Device                                                                                                                                           |                                                   Home Assistant                                                    | Notes                                                                                                                    |
|--------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------:|--------------------------------------------------------------------------------------------------------------------------|
| [Mercedes GLA](https://www.mercedes-benz.com/en/vehicles/passenger-cars/gla/)                                                                    |                             [mercedesme2020](https://github.com/ReneNulschDE/mbapi2020)                             | Custom integration managed via HACS                                                                                      |
| [Keba P30 Connect](https://www.keba.com/en/emobility/products/c-series/c-series) wallbox                                                         |                              [Keba](https://www.home-assistant.io/integrations/keba/)                               | Charging station connected via LAN and Unifi U6 using brigde mode                                                        |

#### Other devices and virtual sensors

| Device / Sensor                                                                                                                   |                                        Home Assistant                                        | Notes                                                                                                                                                          |
|-----------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Neato Botvac D7](https://neatorobotics.com/)                                                                                     |                  [Neato](https://www.home-assistant.io/integrations/neato/)                  | Robot number 1, not much to say, does the job. Actually so good, we now have two of them ;-)                                                                   |
| [Worx Landroid S](https://worx-europe.com/)                                                                                       |                    [REST](https://www.home-assistant.io/components/rest/)                    | Robot number 2, we call it "Shaun". This little guy is integrated via Landroid cloud API                                                                       |
| [Hunter Pro-HC](https://www.hunterindustries.com/en-metric/irrigation-product/controllers/pro-hc)                                 |          [Hunter Hydrawise](https://www.home-assistant.io/integrations/hydrawise/)           | Controls watering of the lawn and plants around the house.                                                                                                     |
| Mailbox via 2 [Xiaomi Aqara Window Door Sensor](https://xiaomi-mi.com/sockets-and-sensors/xiaomi-aqara-window-door-sensor/)       |                  [deCONZ](https://www.home-assistant.io/components/deconz/)                  | Detect opening of the mailbox flap or door                                                                                                                     |
| ESPHome Watertank Sensor                                                                                                          |                [ESPHome](https://www.home-assistant.io/integrations/esphome/)                | To measure the water level of our garden cistern to ensure that our plants always get enough water.                                                            |
| Waste Collection Sensor                                                                                                           |    [Waste Collection Schedule](https://github.com/mampfes/hacs_waste_collection_schedule)    | Waste collection integration reminds us not to forget the garbage cans. Works well with the iCal Calender provided by our local garbage disposal company.      |

[home-assistant]: https://home-assistant.io
[home-assistant-shield]: https://img.shields.io/badge/Home%20Assistant-2021.12.6-blue
[esphome-shield]: https://img.shields.io/badge/esphome.io-2021.12.0-green
[license-shield]: https://img.shields.io/github/license/mhaack/home-assistant-config.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2021.svg
[circleci-shield]: https://img.shields.io/circleci/project/github/mhaack/home-assistant-config/master.svg
[circleci]: https://circleci.com/gh/mhaack/workflows/home-assistant-config
[commits]: https://github.com/mhaack/home-assistant-config/commits/master
[commits-shield]: https://img.shields.io/github/commit-activity/m/mhaack/home-assistant-config
[last-commit-shield]: https://img.shields.io/github/last-commit/mhaack/home-assistant-config.svg
[twitter]: http://twitter.com/mhaack
[twitter-badge]: https://img.shields.io/twitter/follow/mhaack.svg?style=social
