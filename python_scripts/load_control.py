#
# load_control.py
#

def min(x,y):
    if x < y:
        return x
    return y
        
def max(x,y):
    if x > y:
        return x
    return y

#
# Get the temperature but use the saved setpoint if there is a mismatch
#
def get_setpoint(location, hass, logger):
    good=0
    if location == 'upstairs':
        name = 'climate.upstairs'
        saved = 'input_number.upstairs_setpoint'
        good=1
    elif location == 'downstairs':
        name = 'climate.downstairs'
        saved = 'input_number.downstairs_setpoint'
        good=1
    else:
        logger.error("Set temperature called for bad location {}.".format(location))

    if good:
        saved_setpoint = int(float(hass.states.get(saved).state)) # 70
        current_setpoint = hass.states.get(name).attributes['temperature']
        #if saved_setpoint <= 65:
        #    logger.info("Initializing {} to {}.".format(name, current_setpoint))
        #    # set input_number here
        #    new_setpoint=current_setpoint
        #    setpoint_arg = {'entity_id': saved,
        #                    'value': new_setpoint}
        #    hass.services.call('input_number', 'set_value', setpoint_arg)
        #    saved_setpoint = new_setpoint
        #    logger.info('{} set to {}'.format(saved, new_setpoint))
        #    # end set input_number
        if saved_setpoint != current_setpoint:
            # check for initialization
            logger.warn("Saved temp for {} {} but current {}.".format(name,
                                                                      saved_setpoint,
                                                                      current_setpoint))
    return saved_setpoint
    
#
# main
#
# debug mode is default
debug = int(data.get('debug', 1))
    
kWH_limit = float(hass.states.get('input_number.kwh_limit').state) # 2.0

# Get energy levels
demand_60 = float(hass.states.get('sensor.1_hr_demand').state)
demand_40 = float(hass.states.get('sensor.medium_long_demand').state)
demand_20 = float(hass.states.get('sensor.medium_demand').state)
demand_10 = float(hass.states.get('sensor.fast_demand').state)

logger.info("limit: {:.2f}, demand: 60: {:.2f}, 40: {:.2f}, 20: {:.2f}, 10: {:.2f}".format(kWH_limit, demand_60,demand_40,demand_20,demand_10))

# Get thermostat settings
us_setpoint=get_setpoint('upstairs',hass,logger)
ds_setpoint=get_setpoint('downstairs',hass,logger)

logger.info("current setpoints: ds {}, us {}".format(ds_setpoint, us_setpoint))

# Estimate what the hourly demand will be if we decrement a degree. Assume that
# decrementing one thermostat will cost about 3 kWH
bump_demand_20=3.0
bump_demand=(2*demand_40+bump_demand_20)/3.0
logger.info("Estimated bump demand: {:.2f}".format(bump_demand))

# Figure out if we need to change the temperature
delta_t = 0
if demand_20 > kWH_limit:
    logger.info("Suggesting temperature increment")
    delta_t = delta_t + 1
if bump_demand < kWH_limit:
    logger.info("Suggesting temperature decrement")
    delta_t = delta_t - 1

# Handle any change
if delta_t == 0:
    logger.info("No Change")
else:
    new_us_setpoint=us_setpoint
    new_ds_setpoint=ds_setpoint
    # adjust one thermostat at a time, keeping the upstairs higher or equal
    if delta_t > 0:
        # Increment but not past the target_hi
        target_hi = int(float(hass.states.get('input_number.hi_temp').state)) # 80
        if us_setpoint < ds_setpoint:
            new_us_setpoint = min(us_setpoint + delta_t, target_hi)
        else:
            new_ds_setpoint = min(ds_setpoint + delta_t, target_hi)
    else:
        # Decrement but not below the target_temp
        target_temp = int(float(hass.states.get('input_number.target_temp').state)) # 70
        if us_setpoint < ds_setpoint:
            new_ds_setpoint = max(ds_setpoint + delta_t, target_temp)
        else:
            new_us_setpoint = max(us_setpoint + delta_t, target_temp)

    logger.info("New settings: ds {}, us {}".format(new_ds_setpoint, new_us_setpoint))

    # Set the new temperatures
    hass.services.call('python_script','set_temp',{'location':'upstairs',
                                                   'setpoint':new_us_setpoint,
                                                   'debug':debug})

    hass.services.call('python_script','set_temp',{'location':'downstairs',
                                                   'setpoint':new_ds_setpoint,
                                                   'debug':debug})
