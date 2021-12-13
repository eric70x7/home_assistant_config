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
demand_55 = float(hass.states.get('sensor.55_min_peak_time_demand').state)
demand_25 = float(hass.states.get('sensor.25_min_peak_time_demand').state)
demand_5 = float(hass.states.get('sensor.5_min_peak_time_demand').state)

ac_on = int(hass.states.get('sensor.upstairs_cooling').state) or int(hass.states.get('sensor.downstairs_cooling').state)

logger.info("___________________________________________________________________________")
logger.info("limit: {:.2f}, demand: 60: {:.2f}, 55: {:.2f}, 25: {:.2f}, 5: {:.2f}".format(kWH_limit, demand_60,demand_55,demand_25,demand_5))
logger.info("ac_on: {:}".format(ac_on))

# The instantaneous demand of both ACs is about 8-10kW
ac_consumption=9

# Predict what the demand will be if we turn on the AC for the next 5 mins
predicted_demand=(11.0*demand_55+ac_consumption)/12.0
allowable_demand=kWH_limit-predicted_demand
allowable_duration=(5.0/60.0)+allowable_demand/ac_consumption
allowable_duration_secs = int(3600*allowable_duration)
hass.services.call('input_number', 'set_value', {'entity_id': 'input_number.predicted_demand_50',
                                                 'value' : predicted_demand})
logger.info("55: pred: {:.2f} kWh, allow: = {:.2f} kWh, dur: = {:.2f} min".format(predicted_demand, allowable_demand, 60*allowable_duration))

predicted_demand=(5.0*demand_25+ac_consumption)/6.0
allowable_demand=kWH_limit-predicted_demand
allowable_duration=(5.0/60.0)+allowable_demand/ac_consumption
allowable_duration_secs = int(3600*allowable_duration)
hass.services.call('input_number', 'set_value', {'entity_id': 'input_number.predicted_demand_30',
                                                 'value' : predicted_demand})
logger.info("25: pred: {:.2f} kWh, allow: = {:.2f} kWh, dur: = {:.2f} min".format(predicted_demand, allowable_demand, 60*allowable_duration))

# Don't start the AC unless it can run for a minimum time
min_run_secs = 5.1*60

if allowable_duration_secs <= 0 or demand_60 >= kWH_limit:
  # If the allowable run time is less than zero, finish the timer now
  logger.info("Finishing timer.")
  hass.services.call('timer', 'finish', {'entity_id' : 'timer.ac_run_timer'})

  #hi_temp = int(float(hass.states.get('input_number.hi_temp').state)) # 70

  # Make sure we're at the hi setpoint
  #hass.services.call('python_script','set_temp',{'location':'upstairs',
  #                                               'setpoint':hi_temp,
  #                                               'debug':debug})

  #hass.services.call('python_script','set_temp',{'location':'downstairs',
  #                                               'setpoint':hi_temp,
  #                                               'debug':debug})

elif ac_on or (allowable_duration_secs > min_run_secs):
  logger.info("Starting timer {}".format(allowable_duration_secs))
  hass.services.call('timer', 'start', {'entity_id' : 'timer.ac_run_timer',
                                        'duration': allowable_duration_secs})
  
  precool_temp = int(float(hass.states.get('input_number.precool_temp').state)) # 70

  # Set the new temperatures
  hass.services.call('python_script','set_temp',{'location':'upstairs',
                                                 'setpoint':precool_temp,
                                                 'debug':debug})

  hass.services.call('python_script','set_temp',{'location':'downstairs',
                                                 'setpoint':precool_temp,
                                                 'debug':debug})

logger.info("___________________________________________________________________________")
