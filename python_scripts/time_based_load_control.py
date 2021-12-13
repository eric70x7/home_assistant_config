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
    
# override sensor with argument
sensor_kWH_limit = float(hass.states.get('input_number.kwh_limit').state)
kWH_limit = float(data.get('kWH_limit', sensor_kWH_limit))

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

if demand_20 > kWH_limit:
    logger.info("Cooling OFF")
    target_hi = int(float(hass.states.get('input_number.hi_temp').state)) # 80
    new_us_setpoint = target_hi
    new_ds_setpoint = target_hi
else:
    logger.info("Cooling ON")
    precool_temp = int(float(hass.states.get('input_number.precool_temp').state)) # 70
    new_us_setpoint = precool_temp
    new_ds_setpoint = precool_temp

logger.info("New settings: ds {}, us {}".format(new_ds_setpoint, new_us_setpoint))

# Set the new temperatures
hass.services.call('python_script','set_temp',{'location':'upstairs',
                                               'setpoint':new_us_setpoint,
                                               'debug':debug})

hass.services.call('python_script','set_temp',{'location':'downstairs',
                                               'setpoint':new_ds_setpoint,
                                               'debug':debug})
