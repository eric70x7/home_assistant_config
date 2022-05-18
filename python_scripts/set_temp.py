
# Setter interfaces

# 
# Set cool temp for Trane thermostat when hvac_mode is heat_cool
#
def set_cool_temp(thermostat, setpoint):
    if thermostat:
        # Handle setting the heat and cool settings in heat_cool mode
        low_setpoint=thermostat.attributes['target_temp_low']

        logger.info(f"Setting {thermostat.entity_id} cool to {setpoint}.")

        hass.services.call('climate','set_temperature',{'entity_id':thermostat.entity_id,
                                                        'target_temp_high': setpoint,
                                                        'target_temp_low': low_setpoint})

#
# Set heat temp for Trane thermostat when hvac_mode is heat_cool
#
def set_heat_temp(thermostat, setpoint):
    if thermostat:
        # Handle setting the heat and cool settings in heat_cool mode
        high_setpoint=thermostat.attributes['target_temp_high']

        logger.info(f"Setting {thermostat.entity_id} heat to {setpoint}.")

        hass.services.call('climate','set_temperature',{'entity_id':thermostat.entity_id,
                                                        'target_temp_high': high_setpoint,
                                                        'target_temp_low': setpoint})

#
# Set temp for Trane thermostat when hvac_mode is heat, cool or off
#
def set_single_temp(thermostat, setpoint):
    if thermostat:
        logger.info(f"Set {thermostat.entity_id} temperature to {setpoint}.")
        # This will apply if the thermostat is in either heat OR cool OR none hvac_mode
        hass.services.call('climate','set_temperature',{'entity_id':thermostat.entity_id,
                                                        'temperature': setpoint})

#
# Return a temperature setter according to the current mode
#
def get_temp_setter(thermostat, set_heat):
    rval = None
    if thermostat.state == 'heat_cool':
        if set_heat:
            rval=set_heat_temp
        else:
            rval=set_cool_temp
    else:
        rval=set_single_temp
    return rval

#
# Set the temperature main code
#

# debug mode is default
debug = int(data.get('debug', 1))

# name can be upstairs or downstairs
location = data.get('location')
setpoint = data.get('setpoint')
set_heat = data.get('set_heat', 0)

# Get the thermostat state object
# See https://www.home-assistant.io/docs/configuration/state_object/
thermostat=None

if location == 'upstairs':
    thermostat = hass.states.get('climate.upstairs_trane_thermostat')
elif location == 'downstairs':
    thermostat = hass.states.get('climate.downstairs_trane_thermostat')
else:
    logger.error(f"Set temperature called for bad location {location}.")

set_temp=get_temp_setter(thermostat, set_heat)

# set the temperature
if not debug:
    set_temp(thermostat, setpoint)
else:
    logger.info("Debug mode or bad entity state. No change made.")
