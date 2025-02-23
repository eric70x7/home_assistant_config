import appdaemon.plugins.hass.hassapi as hass
import math
import datetime
""" 
import pytz
"""
#
# Control the taper of a dimmable light
#
# Args:
#

class LogLight(hass.Hass):

  def initialize(self):
    self.log_light=self.get_entity(self.args["log_light_entity"])
    self.real_light=self.get_entity(self.args["real_light_entity"])
    self.log_light.listen_state(self.update_brightness, attribute = "brightness")
    self.log_light.listen_state(self.update_real_state, attribute = "state")
    self.real_light.listen_state(self.update_log_state, attribute = "state")
    # self.real_light.listen_state(self.update_log_state, attribute = "state")
    self.range=255
    
    '''Sync the initial state according to the real light current state'''
    if self.real_light.get_state() == "on":
      self.log_light.call_service("turn_on")
    else:
      self.log_light.call_service("turn_off")

  '''
  Generic log for state listeners
  '''
  def logit(self, entity, attribute, old, new):
    self.log(f"{entity}[{attribute}]: Was {old}, changed to {new}.")

  '''
  Keep the states in sync
  '''
  def update_real_state(self, entity, attribute, old, new, cb_args):
    if not new == self.real_light.get_state():
      if new == "off":
        self.real_light.call_service("turn_off")
      else:
        self.real_light.call_service("turn_on")
    
  '''
  Keep the states in sync
  '''
  def update_log_state(self, entity, attribute, old, new, cb_args):
    if not new == self.log_light.get_state():
      if new == "off":
        self.log_light.call_service("turn_off")
      else:
        self.log_light.call_service("turn_on")
    
  '''
  Adjust the brightness
  '''
  def update_brightness(self, entity, attribute, old, new, cb_args):
    # self.logit(entity, attribute, old, new)
    if(new == None or new <= 0):
      output=0
    else:
      output= int(self.range*math.pow(new/self.range,3))
    
    self.real_light.call_service("turn_on", brightness=output)