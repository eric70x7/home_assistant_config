import appdaemon.plugins.hass.hassapi as hass

#
# Report thermostats
#
# Args:
#

class ReportThermostats(hass.Hass):

  def initialize(self):
    # for some reason this gets called for either thermostat, though downstairs is specified
    self.listen_state(self.therm_changed, entity='climate.downstairs_trane_thermostat', attribute='temperature')
    self.log(f"ReportThermostats initialized")

  def therm_changed(self, entity, attribute, old, new, cb_args):
    self.log(f"{entity} changed from {old} to {new}.")
