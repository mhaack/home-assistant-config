VERSION = '1.0.0'

DISPLAY_ADDRESS = 'NEQ0711284'
DISPLAY_LINE_1 = 'Fenster/Tür'
DISPLAY_LINE_2 = 'Haus'
DISPLAY_LINE_3 = 'Hütte'
DISPLAY_LED = 'green'

led = data.get('led', DISPLAY_LED)
beep = data.get('beep', 'short_short')

if hass.states.is_state('group.all_contact_sensors', 'on'):
    icon1 = 'open'
else:
    icon1 = 'closed'

if hass.states.is_state('alarm_control_panel.alarm_haus', 'disarmed'):
    icon2 = 'error'
elif hass.states.is_state('alarm_control_panel.alarm_haus', 'pending'):
    icon2 = 'service'
elif hass.states.is_state('alarm_control_panel.alarm_haus', 'triggered'):
    icon2 = 'info'
else:
    icon2 = 'ok'

if hass.states.is_state('alarm_control_panel.alarm_carport', 'disarmed'):
    icon3 = 'error'
elif hass.states.is_state('alarm_control_panel.alarm_carport', 'pending'):
    icon3 = 'service'
elif hass.states.is_state('alarm_control_panel.alarm_carport', 'triggered'):
    icon3 = 'info'
else:
    icon3 = 'ok'

display_data = {'address': DISPLAY_ADDRESS, 'line1':DISPLAY_LINE_1, 'line2':DISPLAY_LINE_2, 'line3':DISPLAY_LINE_3, 'icon1': icon1, 'icon2': icon2, 'icon3':icon3, 'led': led, 'beep': beep}
hass.services.call('python_script', 'update_display', display_data)