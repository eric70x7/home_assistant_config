import appdaemon.plugins.hass.hassapi as hass

class EntityListener(hass.Hass):
    def initialize(self):
      ss=self.args["substr"]
      all_entities = self.get_state()
      entities_to_listen=[e for e in all_entities if ss in e]
      for e in entities_to_listen:
          self.listen_state(self.log_state_change, e)
        
    '''
    Generic log for state listeners
    '''
    def logit(self, entity, old, new):
      self.log(f"{entity}: Was {old}, changed to {new}.")

    def log_state_change(self, entity, attribute, old, new, kwargs):
        self.logit(entity, old, new)