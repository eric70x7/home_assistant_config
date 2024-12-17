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
    self.volume_increment = 0.08
    self.volume_update_interval = datetime.timedelta(seconds=1)
    self.volume_changed = True
    self.next_volume_change = datetime.datetime.now()
    self.listen_state(self.family_room_tv_volume_up,   entity_id=self.volume_up_trigger)
    self.listen_state(self.family_room_tv_volume_down, entity_id=self.volume_down_trigger)
    self.listen_state(self.family_room_tv_volume_set,  entity_id=self.volume_knob)
    self.listen_state(self.track_tv_remote_volume,     entity_id=self.volume_remote, attribute='volume_level')
#    for e in self.audio_channels:
#      self.listen_state(self.log_volume_changed, entity_id=e, attribute='volume_level')
    self.log(f"VolumeController initialized")

  def logit(self, entity, old, new):
    self.log(f"{entity}: Was {old}, changed to {new}.")

  def log_volume_change(self, entity, attribute, old, new, cb_args):
    self.logit(entity, old, new)

  def track_tv_remote_volume(self, entity, attribute, old, new, cb_args):
    # self.logit(entity, old, new)
    self.set_volume_knob(new)

  def set_vols(self, nv):
    now=datetime.datetime.now()
    if self.volume_changed and (now > self.next_volume_change):
      self.next_volume_change = now + self.volume_update_interval
      for e in self.audio_channels:
        self.call_service("media_player/volume_set", entity_id=e, volume_level=nv)
      self.volume_changed = False

  def set_volume_knob(self, nv):
    if nv < 0.0:
      nv = 0.0
    elif nv > 1.0:
      nv = 1.0
    self.call_service("input_number/set_value", entity_id=self.volume_knob, value=nv)
    self.volume_changed = True

  def get_volume_knob(self):
    return float(self.get_state(self.volume_knob))

  def family_room_tv_volume_set(self, entity, attribute, old, new, cb_args):
    self.set_vols(float(new))

  def family_room_tv_volume_down(self, entity, attribute, old, new, cb_args):
    if new == "on":
      self.turn_off(entity)
      self.set_volume_knob(self.get_volume_knob() - self.volume_increment)

  def family_room_tv_volume_up(self, entity, attribute, old, new, cb_args):
    if new == "on":
      self.turn_off(entity)
      self.set_volume_knob(self.get_volume_knob() + self.volume_increment)



