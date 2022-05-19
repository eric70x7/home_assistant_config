#
# load_control.py
#

# debug mode is default
debug = int(data.get('debug', 1))
    
# override sensor with argument
sensor_kWH_limit = float(hass.states.get('input_number.kwh_limit').state)
kWH_limit = float(data.get('kWH_limit', sensor_kWH_limit))

# Get energy levels
demand_60 = float(hass.states.get('sensor.1_hr_peak_time_demand').state)
demand_55 = float(hass.states.get('sensor.55_min_peak_time_demand').state)
demand_25 = float(hass.states.get('sensor.25_min_peak_time_demand').state)
demand_5  = float(hass.states.get('sensor.5_min_peak_time_demand').state)

logger.info("___________________________________________________________________________")
logger.info("limit: {:.2f}, demand: 60: {:.2f}, 55: {:.2f}, 25: {:.2f}, 5: {:.2f}".format(kWH_limit, demand_60,demand_55,demand_25,demand_5))

# Get thermostat settings
us_setpoint=float(hass.states.get('sensor.upstairs_cool_setpoint').state)
ds_setpoint=float(hass.states.get('sensor.downstairs_cool_setpoint').state)
logger.info(f"Current setpoints: ds {ds_setpoint}, us {us_setpoint}")

if demand_55 > kWH_limit or demand_25 > kWH_limit:
    logger.info("Cooling OFF")
    new_setpoint = int(float(hass.states.get('input_number.hi_temp').state)) # 80
else:
    logger.info("Cooling ON")
    new_setpoint = int(float(hass.states.get('input_number.target_temp').state)) # 70

logger.info(f"New setting: {new_setpoint}")

# Set the new temperatures
hass.services.call('python_script','set_temp',{'location':'all',
                                               'setpoint':new_setpoint,
                                               'debug':debug})