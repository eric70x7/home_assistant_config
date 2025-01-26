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
    self.log_light.listen_state(self.update_state, attribute = "state")
    self.range=255

  '''
  Generic log for state listeners
  '''
  def logit(self, entity, attribute, old, new):
    self.log(f"{entity}[{attribute}]: Was {old}, changed to {new}.")

  '''
  Turn on/off
  '''
  def update_state(self, entity, attribute, old, new, cb_args):
    # self.logit(entity, attribute, old, new)
    if new == "off":
      self.real_light.call_service("turn_off")
    else:
      self.real_light.call_service("turn_on")
    
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