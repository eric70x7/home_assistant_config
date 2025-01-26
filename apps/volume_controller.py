import appdaemon.plugins.hass.hassapi as hass
import math
import datetime
""" 
import pytz
"""
#
# Control TV and associated media player volumes
#
# Args:
#

class VolumeController(hass.Hass):

  def initialize(self):
    self.volume_knob='input_number.family_room_tv_volume_knob'
    self.volume_remote='media_player.family_room_tv'
    self.volume_up_trigger='input_boolean.family_room_tv_volume_up'
    self.volume_down_trigger='input_boolean.family_room_tv_volume_down'
    self.audio_channels= ['media_player.xantech8_center',
                          'media_player.xantech8_front',
                          'media_player.xantech8_rear']
    self.volume_increment = float(self.get_state(self.volume_knob, attribute='step'))
    # self.log(f"step = {self.volume_increment}")
    self.volume_limit = 0.75

    self.listen_state(self.volume_up,              entity_id=self.volume_up_trigger)
    self.listen_state(self.volume_down,            entity_id=self.volume_down_trigger)
    self.listen_state(self.set_entity_vols,        entity_id=self.volume_knob)
    self.listen_state(self.track_tv_remote_volume, entity_id=self.volume_remote, attribute='volume_level')
#    for e in self.audio_channels:
#      self.listen_state(self.log_volume_change,    entity_id=e, attribute='volume_level')
    ''' Show all available services '''
#    ss = self.list_services()
#    for s in ss:
#      self.log(f"{s}")
    self.log(f"VolumeController initialized")

  '''
  Generic log for state listeners
  '''
  def logit(self, entity, old, new):
    self.log(f"{entity}: Was {old}, changed to {new}.")

  '''
  Show volume changes
  '''
  def log_volume_change(self, entity, attribute, old, new, cb_args):
    self.logit(entity, old, new)

  '''
  Adjust volume setting based on remote
  '''
  def track_tv_remote_volume(self, entity, attribute, old, new, cb_args):
    # self.logit(entity, old, new)
    self.set_volume_knob(new)

  '''
  When the volume setting changes, change the volume
  '''
  def set_entity_vols(self, entity, attribute, old, new, cb_args):
    '''
    Only apply the volume if it crosses a multiple of the volume_increment.
    Increments smaller than the volume resolution of the entity have no effect
    and applying them just increases the latency.
    '''
    if (float(old)//self.volume_increment != float(new)//self.volume_increment):
#      self.log(f"Applying volume change {old} -> {new} ({float(old)//self.volume_increment} != {float(new)//self.volume_increment})")
      nv = max(0.0, min(float(new),self.volume_limit))
      for e in self.audio_channels:
        self.call_service("media_player/volume_set", entity_id=e, volume_level=nv)
#    else:
#      self.log(f"Inhibiting volume change {old} -> {new} ({float(old)//self.volume_increment} == {float(new)//self.volume_increment})" )

  '''
  Change the volume setting.  Changes to this entity trigger setting of the 
  audio entities
  '''
  def set_volume_knob(self, nv):
    if nv != None:
      self.call_service("input_number/set_value", entity_id=self.volume_knob, value=nv)

  '''
  Get the current volume setting
  '''
  def get_volume_knob(self):
    return float(self.get_state(self.volume_knob))

  '''
  Increment the volume setting down
  '''
  def volume_down(self, entity, attribute, old, new, cb_args):
    if new == "on":
      self.turn_off(entity)
      ''' input_number/decrement is not available '''
      self.set_volume_knob(self.get_volume_knob() - self.volume_increment)

  '''
  Increment the volume setting up
  '''
  def volume_up(self, entity, attribute, old, new, cb_args):
    if new == "on":
      self.turn_off(entity)
      ''' input_number/increment is not available '''
      self.set_volume_knob(self.get_volume_knob() + self.volume_increment)
