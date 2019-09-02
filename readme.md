# JaMa Villa Home Assistant Configuration

![Project Maintenance][maintenance-shield]
[![Home Assistant][home-assistant-shield]](home-assistant)
[![License][license-shield]](LICENSE)

[![Circle CI][circleci-shield]][circleci]
[![GitHub Activity][commits-shield]][commits]
[![GitHub Last Commit][last-commit-shield]][commits]

[![Twitter][twitter-badge]][twitter]

Here's our JaMa Villa Home Assistant configuration, running our home
automations. [Home Assistant][home-assistant] (HA) is an open-source home
automation platform which allows you to control devices easily, track multiple
sensors and integrate with a wide variety of commercial & DIY solutions.
I currently run it via [Hass.io](https://www.home-assistant.io/hassio/) on
a single Raspberry Pi. My HA configuration structure is heavily inspired by
the work done by [Franck Nijhof](https://github.com/frenck)

![HA](img/header.png "header")

I try regularly update my configuration files, there is always something to
tweak or improve 😉. This repository is to inspire others, be free to use the
code from this repo for your own HA setup. If you think it is helpful and like
anything here, Be sure to 🌟 the GitHub repo.

## System Overview

## House Automation Hardware

### Host System

My Home Assistant system currently run's on a Raspberry PI 3 with 16GByte SanDisk Extrem microSD card. All is managent by hass.io and the following add-ons are currentyl used:

* [AdGuard Home](https://github.com/hassio-addons/addon-adguard-home)
* [Configurator](https://home-assistant.io/addons/configurator) - would like to use the VSC add-on but that is not avilable on Raspberry PI
* [Grafana](https://github.com/hassio-addons/addon-grafana)
* [InfluxDB](https://github.com/hassio-addons/addon-influxdb)
* [Log Viewer](https://github.com/hassio-addons/addon-log-viewer)
* [Mosquitto MQTT broker](https://home-assistant.io/addons/mosquitto/)
* [SSH & Web Terminal](https://github.com/hassio-addons/addon-ssh)
* [Samba share](https://home-assistant.io/addons/samba/)

#### Hubs

| Device        | Home Assistant     | Notes      |
| ------------- |:------------------:| ---------- |
| [Homematic CCU3](https://amzn.to/2HyzEBK) | [Homematic](https://www.home-assistant.io/components/homematic/) | Used to controll all Homematic devices |
| [deCONZ Conbee II](https://amzn.to/2PoKl0g) | [deCONZ](https://www.home-assistant.io/components/deconz/) | The main ZigBee Hub |
| [Philips Hue Bridge](https://amzn.to/2UdvVP8) | [Philips Hue](https://www.home-assistant.io/components/hue/) | Used to control all Philips Hue smart bulbs |

#### Network

| Device  | Quantity | Home Assistant | Notes |
| ------------- | :---: | ------------- | ------------- | ------------- |
| [Ubiquiti Networks UniFi Switch - 16 Ports (US-16-150W)](https://amzn.to/2PjIFox) | 1 | [Ubiquiti Unifi](https://www.home-assistant.io/components/unifi/) | Primary network switch |
| [Ubiquiti Networks Unifi AP Lite (UAP-AC-LITE)](https://amzn.to/2zswivK) | 2 | [Ubiquiti Unifi](https://www.home-assistant.io/components/unifi/) | Wireless Access Point for interior use. |
| [Ubiquiti Unifi Security Gateway (USG)](https://amzn.to/2Lg4vEd) | 1 | [Ubiquiti Unifi](https://www.home-assistant.io/components/unifi/) | Main router & firewall device |
| [Draytek Vigor 130 ADSL/VDSL modem](https://amzn.to/2NJI4Kv) | 1  | n/a | The connection to the outside world |

On network gear we are all-in for Unifi devices, they provide the a reliable and stable network for our house. The Draytek modem is connects us to the DSL line of the internet provider. The Unifi network equipment is also used as of one theprimary presence detection methods.

#### Lighting

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|
Hue Lampen 3
Hue Stripes 2
Paulman RGBW Controller ZigBee 1

#### Outlets & Switches

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|
| [Wireless Switch Actuator 1-channel with power metering (HM-ES-PMSw1-Pl-DN-R1)](https://amzn.to/2ZqGkwZ) | 3 | [Homematic Switch](https://www.home-assistant.io/components/homematic/) | Indoor outlet for selected devices, mainly for power metering |
| [Wireless Switch Actuator 1-channel, flush-mount (HM-LC-Sw1-FM)](https://amzn.to/2L7z2p2) | 1 | [Homematic Switch](https://www.home-assistant.io/components/homematic/) | Hallway light switch |
| [Wireless Switch Actuator 1-channel, DIN-rail mount (HM-LC-Sw1-DR)](https://amzn.to/2L8Jv3p) | 4 | [Homematic Switch](https://www.home-assistant.io/components/homematic/) | Used to control outdoor |
| [Wireless Switch Actuator 2-channel with power metering, DIN-rail mount (HM-ES-PMSw1-DR)](https://amzn.to/2NMf2tA) | 4 | [Homematic Switch](https://www.home-assistant.io/components/homematic/) | Used to control pumps of the pool and water tank |
| [Wireless Switch Actuator 4-channel, DIN-rail mount (HM-LC-Sw4-DR)](https://amzn.to/2ZrPUPZ) | 1 |[Homematic Switch](https://www.home-assistant.io/components/homematic/) | Used to control outdoor and pool lighting |
| [Sonoff S20 Smart Socket](https://amzn.to/2Znqe7f) | 8 |[MQTT Switch](https://www.home-assistant.io/components/switch.mqtt/) | The main christmas season light driver |
| [Sonoff 4CH Pro R2](https://amzn.to/2LbEIhT) | 1 |[MQTT Switch](https://www.home-assistant.io/components/switch.mqtt/) | Used to control outdoor garden low power lighting |
| [Sonoff TH16](https://amzn.to/2L8EVlF) | 1 |[MQTT Switch](https://www.home-assistant.io/components/switch.mqtt/) | Carport light and outdoor temperature & humidity with Si7021 sensor |

Switches and outlets are used in various capacities, most are for lighting and some are for pool & pump devices. For devices consuming more energy I prefer the Homematic devices, they give a good and secure overall impression. For seasonal cristmas lighting (most are low power LEDs) I mainly use Sonoff outlets.

#### Sensors

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|
| [Wireless Differential Temperature Sensor (HM-WDS30-OT2-SM)](https://amzn.to/2PnlppL) | 2 | [Homematic Sensor](https://www.home-assistant.io/components/homematic/) | Pool & solar temperature sensor for pool automation |
| [Xiaomi Aqara Smart Temperature Humidity Sensor](https://amzn.to/2ZqKXac) | 6 | [deCONZ Sensor](https://www.home-assistant.io/components/deconz/#sensor) | Main indoor temperature & humidity sensor |
| [Xiaomi Aqara Smart Vibration Sensor](https://amzn.to/2zwhQCX) | 2 | [deCONZ Sensor](https://www.home-assistant.io/components/deconz/#sensor) | Moving detection of our garden bench ;-) |
| [Sonoff TH16](https://amzn.to/2L8EVlF) with Si7021 sensor | 1 |[MQTT Switch](https://www.home-assistant.io/components/switch.mqtt/) | Garden & outdoor temperature & humidity sensor |

Most of the sensor got replaced with Xiaomi Aqara devices recently, they are small and very reliabale, connected via ZigBee deCONZ. Unfortunatelly they are only for indoor use, so I keep the Homematic HM-WDS30-OT2-SM for outdoor.

#### Security

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|
| [Wireless Door/Window Sensor, optical (HM-Sec-SCo)](https://amzn.to/2HxLPim) | 9 | [Homematic Binary Sensor](https://www.home-assistant.io/components/homematic/) | Door sensors to detect if windows & exterior doors have been opened / closed |
| [Wireless Shutter Contact (HM-Sec-SC-2)](https://amzn.to/2zwj1Cw) | 1 | [Homematic Binary Sensor](https://www.home-assistant.io/components/homematic/) | Door sensors to detect if windows have been opened / closed |
| [Wireless Motion Detector (HM-Sec-MDIR-3)](https://amzn.to/2PnuM97) | 3 | [Homematic Binary Sensor](https://www.home-assistant.io/components/homematic/) | Indoor motion detection |
| [Wireless Siren (HM-Sec-Sir-WM)](https://amzn.to/2ZtDu5q) | 2 | [Homematic Switch](https://www.home-assistant.io/components/homematic/) | Indoor alarm sirene |
| [Rademacher DuoFern Motor Actuator 9471-1](https://amzn.to/2NGKnhC) | 9 | [pyduofern](https://github.com/gluap/pyduofern) (custom component) | Flush-mounted actuator for roller shutter motors |

#### Media

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|

Sonos Players

#### Voice Assistant

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|

Amazon Echo / Alexa

#### Cameras

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|

#### Vacuum

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|

#### Garden

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|

Landorid lawnmower robot


#### Remotes

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|

Duofern
Homematic

#### Other devices

| Device        | Quantity      | Home Assistant     | Notes      |
| ------------- |:-------------:|:------------------:|------------|

Qnap
Fritzbox
Homematic Display

[home-assistant]: https://home-assistant.io
[issue]: https://github.com/mhaack/home-assistant-config/issues
[home-assistant-shield]:https://img.shields.io/badge/Home%20Assistant-0.97.2-blue
[license-shield]: https://img.shields.io/github/license/mhaack/home-assistant-config.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2019.svg
[circleci-shield]: https://img.shields.io/circleci/project/github/mhaack/home-assistant-config/master.svg
[circleci]: https://circleci.com/gh/mhaack/workflows/home-assistant-config
[commits]: https://github.com/mhaack/home-assistant-config/commits/master
[commits-shield]: https://img.shields.io/github/commit-activity/m/mhaack/home-assistant-config.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/mhaack/home-assistant-config.svg
[twitter]: http://twitter.com/mhaack
[twitter-badge]: https://img.shields.io/twitter/follow/mhaack.svg?style=social
