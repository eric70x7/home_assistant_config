import appdaemon.plugins.hass.hassapi as hass
import math
""" 
from datetime import datetime, timezone
import pytz
"""
#
# Report volume changes
#
# Args:
#

class ReportVolume(hass.Hass):

  def initialize(self):
    # self.listen_state(self.vol_changed, entity_id='sensor.center_volume')
    self.listen_state(self.family_room_tv_volume_up,   entity_id='input_boolean.family_room_tv_volume_up')
    self.listen_state(self.family_room_tv_volume_down, entity_id='input_boolean.family_room_tv_volume_down')

    self.volume_increment = 0.08

    self.entities= ['media_player.xantech8_center',
                    'media_player.xantech8_front',
                    'media_player.xantech8_rear']

    for e in self.entities:
      self.listen_state(self.vol_changed, entity_id=e, attribute='volume_level')

    self.log(f"ReportVolume initialized")

  def logit(self, entity, old, new):
    self.log(f"{entity}: Was {old}, changed to {new}.")

  def vol_changed(self, entity, attribute, old, new, cb_args):
    self.logit(entity, old, new)

  def set_vols(self, nv):
    if nv >= 0.0 and nv <= 1.0:
      for e in self.entities:
        cv = self.get_state(entity_id=e, attribute='volume_level')
        self.log(f"Setting {e}: {cv} -> {nv}")
        ''' Set the volume level to the new value '''
        self.call_service("media_player/volume_set", entity_id=e, volume_level=nv)
    
  def current_volume(self):
    ''' Use the current minimum volume for the current volume '''
    cvs = []
    for e in self.entities:
      cvs.append(self.get_state(entity_id=e, attribute='volume_level'))
    return min(cvs)

  def family_room_tv_volume_down(self, entity, attribute, old, new, cb_args):
    if new == "on":
      ''' log the change'''
      # self.logit(entity, old, new)
      
      ''' Toggle the switch back off '''
      self.turn_off(entity)

      ''' Round to nearest volume increment'''
      inc = self.volume_increment
      cv = self.current_volume()
      self.log(f"DOWN: cv = {cv}")
      if cv != None:
        # nv = math.ceil(cv / inc) * inc - inc
        nv = cv - inc
        self.set_vols(nv)


  def family_room_tv_volume_up(self, entity, attribute, old, new, cb_args):
    if new == "on":
      ''' log the change'''
      # self.logit(entity, old, new)
      
      ''' Toggle the switch back off '''
      self.turn_off(entity)

      ''' Round to nearest volume increment'''
      inc = self.volume_increment
      cv = self.current_volume()
      self.log(f"UP: cv = {cv}")
      if cv != None:
        # nv = math.floor(cv / inc) * inc + inc
        nv = cv + inc
        self.set_vols(nv)



