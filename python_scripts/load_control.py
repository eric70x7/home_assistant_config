
kWH_limit = float(hass.states.get('input_number.kwh_limit').state) # 2.0
target_temp = int(float(hass.states.get('input_number.target_temp').state)) # 70
target_hi = int(float(hass.states.get('input_number.hi_temp').state)) # 80

# Get energy levels
demand_60 = float(hass.states.get('sensor.1_hr_demand').state)
demand_15 = float(hass.states.get('sensor.15_min_demand').state)
demand_05 = float(hass.states.get('sensor.5_min_demand').state)

logger.info("demand: {}, {}, {}".format(demand_60,demand_15,demand_05))

# Get thermostat settings
downstairs = 'climate.downstairs'
ds = hass.states.get(downstairs)
ds_setpoint = ds.attributes['temperature']

upstairs = 'climate.upstairs'
us = hass.states.get(upstairs)
us_setpoint = us.attributes['temperature']

logger.info("current setpoints: ds {}, us {}".format(ds_setpoint, us_setpoint))

# Figure out if we need to take action
new_setpoint = us_setpoint
if demand_60 < kWH_limit and demand_15 < kWH_limit and demand_05 < kWH_limit:
    # We're good, bump down the temp
    new_setpoint = us_setpoint-1
    logger.info("All good, decreasing setpoint")
elif demand_05 > kWH_limit:
    if demand_60 > kWH_limit:
        new_setpoint = us_setpoint+1
        logger.info("Hourly demand too high.")
    elif demand_15 > kWH_limit and demand_05 > kWH_limit:
        new_setpoint = us_setpoint+1
        logger.info("5 and 15 both too high.")
    elif demand_05 > 3*kWH_limit:
        new_setpoint = us_setpoint+1
        logger.info("5 is extremely high")

# Make adjustment if any
if new_setpoint != us_setpoint:
    logger.info("Updated setpoint is {}".format(new_setpoint))        

    # limit the range of the adjustments
    if new_setpoint < target_temp:
        new_setpoint = target_temp
        logger.info("Limiting setpoint to lower limit of {}".format(new_setpoint))
    if new_setpoint > target_hi:
        new_setpoint = target_hi
        logger.info("Limiting setpoint to upper limit of {}".format(new_setpoint))
    
    # Make the adjustment
    # THIS CHANGES THE TEMPERATURE BUT IT ALSO DISABLES THE SCHEDULE
    us_temp = {'entity_id': upstairs, 'temperature': new_setpoint}
    hass.services.call('climate', 'set_temperature', us_temp)
    ds_temp = {'entity_id': downstairs, 'temperature': new_setpoint}
    hass.services.call('climate', 'set_temperature', ds_temp)
