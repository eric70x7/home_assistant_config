import appdaemon.plugins.hass.hassapi as hass
import json
import numpy as np
""" 
import pytz
"""
#
# Control energy consumption
#
# Args:
#

class EnergyController(hass.Hass):

  def initialize(self):
    ''' Constants '''
    self.epoch=np.datetime64('1970-01-01')
    self.time_unit=np.timedelta64(1,'s')
    self.energy_sensor='sensor.energy_usage'
    self.energy_hist_name='app.energy_history'

    self.listen_state(self.energy_update, entity_id=self.energy_sensor)

    ''' list of (timestamp, energy) '''
    self.te=[]
    self.set_namespace("energy_namespace")
    # to clear the state:
    # self.set_state(self.energy_hist_name, state=json.dumps(self.te))
    if self.get_state(self.energy_hist_name) != None:
      txt = self.get_state(self.energy_hist_name)
      self.te=[(self.time_unit*int(t),v) for t,v in json.loads(txt)]
    self.set_namespace("default")

    self.ma_times=np.array([np.timedelta64(t,'m') for t in [10, 20, 30, 40, 50, 60]])
    self.max_window=max(self.ma_times) + np.timedelta64(5, 'm')

    # self.log(f"EnergyController initialized")

  '''
  Generic log for state listeners
  '''
  def logit(self, entity, old, new):
    self.log(f"{entity}: Was {old}, changed to {new}.")

  def time_since_epoch(self, t: np.datetime64):
    return t-self.epoch

  '''
  Accumulate usage
  '''
  def energy_update(self, entity, attribute, old, new, cb_args):
    t1=self.time_since_epoch(np.datetime64('now'))
    p=float(new) # watts
    if self.te != []:
      delta_t=t1-self.te[0][0]
      e=p*delta_t/np.timedelta64(1,'h') # watt*hours
      # self.log(f"delta_t = {delta_t}, p = {p}, e = {e}")
      
      ''' Accumulate energy history '''
      self.te.insert(0,(t1, 0))
      self.te = [(t,en+e) for t,en in self.te if t1-t < self.max_window]
      
      ''' Save to namespace '''
      self.set_namespace("energy_namespace")
      save_hist = [(int(t/self.time_unit),v) for t,v in self.te]
      self.set_state(self.energy_hist_name, state=json.dumps(save_hist))
      self.set_namespace("default")

      ''' Interpolate at the desired moving average times '''
      sample_times = np.array([t/self.time_unit for t,_ in self.te]) # convert absolute times to timedeltas
      samples      = np.array([e for _,e in self.te])
      ma_times     = np.array([(t1-t)/self.time_unit for t in self.ma_times])
      ''' x must be increasing '''
      interp_samples = np.flip(np.interp(np.flip(ma_times), np.flip(sample_times), np.flip(samples)))

      # self.log(f'{interp_samples}')

      ''' Update moving average sensors '''
      for t,v in zip(self.ma_times,interp_samples):
        u=v/1000 # kWh
        self.set_state(f"sensor.ad_usage_{int(t/np.timedelta64(1,'m'))}", state=u, attributes={"unit_of_measurement": "kWh"})
