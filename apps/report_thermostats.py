import appdaemon.plugins.hass.hassapi as hass
""" 
from datetime import datetime, timezone
import pytz
"""
#
# Report thermostats
#
# Args:
#

class ReportThermostats(hass.Hass):

  def initialize(self):
    # Listen for temperature changes on both thermostats
    self.listen_state(self.therm_changed, entity_id='climate.downstairs_trane_thermostat', attribute='temperature')
    self.listen_state(self.therm_changed, entity_id='climate.upstairs_trane_thermostat', attribute='temperature')
    self.log(f"ReportThermostats initialized")

  def therm_changed(self, entity, attribute, old, new, cb_args):
    # self.log(f"Entity:   {entity}:")
    # self.log(f"Was {old}, changed to {new}.")

    """ 
    lr = datetime.fromisoformat(self.get_state(entity, attribute='last_reported'))
    self.log(f"Last Reported: {lr.astimezone()}")
    lc = datetime.fromisoformat(self.get_state(entity, attribute='last_changed'))
    self.log(f"Last Changed:  {lc.astimezone()}")
    lu = datetime.fromisoformat(self.get_state(entity, attribute='last_updated'))
    self.log(f"Last Updated:  {lu.astimezone()}")
    """