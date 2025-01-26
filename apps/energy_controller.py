import appdaemon.plugins.hass.hassapi as hass
import math
from pint import UnitRegistry
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
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
    self.ureg = UnitRegistry()
    self.Q_ = self.ureg.Quantity

    self.energy_sensor='sensor.energy_usage'

    self.listen_state(self.energy_update, entity_id=self.energy_sensor)
    self.log(f"EnergyController initialized")

    self.last_energy_time=None

    self.dt = []
    self.p = []

    self.max_window=1.0*self.ureg.hours + 5.0*self.ureg.minutes

  '''
  Generic log for state listeners
  '''
  def logit(self, entity, old, new):
    self.log(f"{entity}: Was {old}, changed to {new}.")

  '''
  Accumulate usage
  '''
  def energy_update(self, entity, attribute, old, new, cb_args):
    t=datetime.now()

    self.logit(entity, old, new)

    p=float(new)*self.ureg.watt
    if self.last_energy_time:
      dt=(t-self.last_energy_time).total_seconds()*self.ureg.sec
      e=p*dt
      self.log(f"dt = {dt:.2f~#P}, p = {p:.2f~#P}, e = {e.to(self.ureg.watt_hour):.2f~#P}")
      self.dt.insert(0,0*self.ureg.sec)
      self.p.insert(0,0*self.ureg.watt)
      '''
      Accumulate
      '''
      self.dt = [dtn + dt for dtn in self.dt if dtn < self.max_window]
      self.p  = [pn + p for pn in self.p][:len(self.dt)]
      mt=[10, 20, 30, 40, 50, 60] * self.ureg.minute

      pddt=self.ureg.Quantity.from_list(self.dt)
      pdp =self.ureg.Quantity.from_list(self.p)
      pdmt=self.ureg.Quantity.from_list(mt)

      s=np.interp(pdmt, pddt, pdp)

      self.log(f"t: {mt}")
      self.log(f"s: {s}")

    df = pd.DataFrame(self.p, index=self.dt)
    # self.log(f"df = {df}")

    self.last_energy_time=t
