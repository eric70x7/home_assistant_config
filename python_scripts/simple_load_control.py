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
# main
#
# debug mode is default
debug = int(data.get('debug', 1))
    
kWH_limit = float(hass.states.get('input_number.kwh_limit').state) # 2.0

# Get energy levels
demand_60 = float(hass.states.get('sensor.1_hr_peak_time_demand').state)
demand_40 = float(hass.states.get('sensor.medium_long_peak_time_demand').state)
demand_20 = float(hass.states.get('sensor.medium_peak_time_demand').state)
demand_10 = float(hass.states.get('sensor.fast_peak_time_demand').state)

logger.info("limit: {:.2f}, demand: 60: {:.2f}, 40: {:.2f}, 20: {:.2f}, 10: {:.2f}".format(kWH_limit, demand_60,demand_40,demand_20,demand_10))

# Get thermostat settings
us_setpoint=float(hass.states.get('sensor.upstairs_cool_setpoint').state)
ds_setpoint=float(hass.states.get('sensor.downstairs_cool_setpoint').state)
logger.info("current setpoints: ds {}, us {}".format(ds_setpoint, us_setpoint))

# Estimate what the hourly demand will be if we decrement a degree. Assume that
# decrementing one thermostat will cost about 3 kWH (changed to 5 with Trane
# thermostats).
bump_demand_20=5.0
bump_demand=(2*demand_40+bump_demand_20)/3.0
logger.info("Estimated bump demand: {:.2f}".format(bump_demand))

# Figure out if we need to change the temperature
delta_t = 0
#if demand_20 > kWH_limit:
#    logger.info("Suggesting temperature increment")
#    delta_t = delta_t + 20
#if bump_demand < kWH_limit:
#    logger.info("Suggesting temperature decrement")
#    delta_t = delta_t - 20

if demand_20 > kWH_limit:
    logger.info("Suggesting temperature increment")
    delta_t = delta_t + 20
else:
    logger.info("Suggesting temperature decrement")
    delta_t = delta_t - 20

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
#        if us_setpoint <= ds_setpoint:
        new_us_setpoint = min(us_setpoint + delta_t, target_hi)
#        else:
        new_ds_setpoint = min(ds_setpoint + delta_t, target_hi)
    else:
        # Decrement but not below the precool_temp
        target_temp = int(float(hass.states.get('input_number.target_temp').state)) # 70
        precool_temp = int(float(hass.states.get('input_number.precool_temp').state)) # 70
#        if us_setpoint <= ds_setpoint:
            # new_ds_setpoint = max(ds_setpoint + delta_t, target_temp)
        new_ds_setpoint = max(ds_setpoint + delta_t, precool_temp)
            # new_ds_setpoint = ds_setpoint + delta_t
#        else:
            # new_us_setpoint = max(us_setpoint + delta_t, target_temp)
        new_us_setpoint = max(us_setpoint + delta_t, precool_temp)
            # new_us_setpoint = us_setpoint + delta_t

    logger.info("New settings: ds {}, us {}".format(new_ds_setpoint, new_us_setpoint))

    # Set the new temperatures
    hass.services.call('python_script','set_temp',{'location':'upstairs',
                                                   'setpoint':new_us_setpoint,
                                                   'debug':debug})

    hass.services.call('python_script','set_temp',{'location':'downstairs',
                                                   'setpoint':new_ds_setpoint,
                                                   'debug':debug})
