VERSION = '1.0.0'

DOMAIN = 'homematic_display'

# Homematic display codes
DATA_START = '0x02'
DATA_STOP = '0x03'
DATA_LINE = '0x12'
DATA_COLOR = '0x11'
DATA_LF = '0x0a'
DATA_ICON = '0x13'
DATA_BEEPER_START = '0x14'
DATA_BEEPER_END = '0x1c'
DATA_BEEPCOUNT_END = '0x1D'
DATA_BEEPINTERVAL_END = '0x16'

DATA_CHANNEL = 3
DATA_PARAM = 'SUBMIT'

# Homematic display dictionaries
DATA_SPECIAL_CHARS = { "d6": "23", "dc": "24", "3d": "27", "c4": "5b", "df": "5f", "e4": "7b", "f6": "7c", "fc": "7d" }
DATA_ICONS = { "off": "0x80", "on": "0x81", "open": "0x82", "closed": "0x83" , "error": "0x84", "ok": "0x85", "info": "0x86", "message": "0x87", "service": "0x88" }
DATA_LEDS = { "off": "0xf0", "red": "0xf1", "green": "0xf2", "orange": "0xf3" }
DATA_BEEPS = { "off": "0xc0", "long_long": "0xc1", "long_short": "0xc2", "long_short_short": "0xc3", "short": "0xc4", "short_short": "0xc5", "long": "0xc6" }

# logger.warning("Update display: {}".format(data))

# get parameters
displayAddress = data.get('address')
displayLines = []
displayLines.append(data.get('line1', ' '))
displayLines.append(data.get('line2', ' '))
displayLines.append(data.get('line3', ' '))
displayIcons = []
displayIcons.append(data.get('icon1', ''))
displayIcons.append(data.get('icon2', ''))
displayIcons.append(data.get('icon3', ''))
led = data.get('led', 'off')
beep = data.get('beep', 'off') 
beepInterval = data.get('beepInterval', 1) # Value in 10 s steps. Allowed values 10 - 160.
beepCount = data.get('beepCount', 1) # Allowed values 0 - 15, 0 means infinite.

# special characters helper
def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

# main rountine
if not displayAddress:
    logger.error('address parameter is missing')
else:
    # start message
    message = []
    message.append(DATA_START)
    message.append(DATA_LF)

    # add lines
    for line, icon in zip(displayLines, displayIcons):
        message.append(DATA_LINE)

        encodedLine = ",".join("0x{:02x}".format(ord(c)) for c in line)
        encodedLine = replace_all(encodedLine, DATA_SPECIAL_CHARS)
        message.append(encodedLine)

        if icon:
            message.append(DATA_ICON)
            message.append(DATA_ICONS.get(icon.lower(), ''))

        message.append(DATA_LF)

    # add beeper
    message.append(DATA_BEEPER_START)
    # append beeper code here
    message.append(DATA_BEEPS.get(beep.lower(), '0xc0'))
    message.append(DATA_BEEPER_END)

    if beepCount == 0:
        beepCount = 16

    message.append(hex(207 + beepCount))
    message.append(DATA_BEEPCOUNT_END)
    message.append(hex(224 + int((beepInterval - 1) / 10)))
    message.append(DATA_BEEPINTERVAL_END)

    # append LED
    message.append(DATA_LEDS.get(led.lower(), 'off'))

    # end message
    message.append(DATA_STOP)

    # logger.warning("Update display message: {}".format(','.join(message)))
    hass.services.call('homematic', 'set_device_value', { 'address': displayAddress, 'channel': DATA_CHANNEL, 'param': DATA_PARAM, 'value': "{}".format(','.join(message)) })
