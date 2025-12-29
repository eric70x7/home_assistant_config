import appdaemon.plugins.hass.hassapi as hass

class Doorbell(hass.Hass):
    def initialize(self):
        # The doorbell entity
        doorbell=self.args["doorbell"]
        
        # List of media players to play on
        self.speakers=self.args["speakers"]
        
        # Listen for doorbell button press
        self.listen_state(self.doorbell_pressed, entity_id=doorbell, new="on")

        # Path to your doorbell chime sound file
        self.chime_sound = self.args["chime"]
        self.doorbell_volume = 0.6
        self.chime_duration = 4

    def doorbell_pressed(self, entity, attribute, old, new, kwargs):
        # Store current states of speakers
        #self.previous_states = {}
        #self.previous_volumes = {}
        
        # Save current states for all speakers
        #for speaker in self.speakers:
        #    self.previous_states[speaker] = self.get_state(speaker)
        #    self.previous_volumes[speaker] = self.get_state(speaker, attribute="volume_level")
        
        #if len(self.speakers) > 1:
        #  self.call_service("media_player/join", entity_id=self.speakers[0], group_members=self.speakers[1:])

        # Set volume for all speakers simultaneously
        #self.call_service(
        #    "media_player/volume_set",
        #    entity_id=self.speakers[0],
        #    volume_level=self.doorbell_volume
        #)
        
        # Play chime on all speakers simultaneously
        self.call_service(
            "media_player/play_media",
            entity_id=self.speakers[0],
            media_content_id=self.chime_sound,
            media_content_type="music",
            announce=True
        )
        
        # Schedule restoration of previous states after chime plays
        # self.run_in(self.restore_states, self.chime_duration)

    def restore_states(self, kwargs):
        # unjoin the speakers if there are more than one
        if len(self.speakers) > 1:
          for speaker in self.speakers:
            self.call_service("media_player/unjoin", entity_id=speaker)

        # Restore previous states and volumes
        for speaker in self.speakers:
            if self.previous_states[speaker] == "playing":
                self.call_service(
                    "media_player/volume_set",
                    entity_id=speaker,
                    volume_level=self.previous_volumes[speaker]
                )
            else:
                self.call_service(
                    "media_player/turn_off",
                    entity_id=speaker
                )


#class Doorbell(hass.Hass):
#    def initialize(self):
#      doorbell=self.args["doorbell"]
#      self.listen_state(self.handle_doorbell, entity_id=doorbell)
#      ''' media player '''
#      self.speakers=self.args["speakers"]
#      self.doorbell_volume=0.8
#      
#      current_volumes = []
#      for speaker in self.speakers:
#        self.log(f'Getting {speaker}')
#        current_volume = float(self.get_state(entity_id=speaker, attribute='volume_level'))
#        current_volumes.append(current_volume)
#        self.log(f"{speaker} volume level is {current_volume}")
#        self.call_service("media_player/volume_set", entity_id=speaker, volume_level=self.doorbell_volume)
#      
#      # join the speakers if there are more than one
#      if len(self.speakers) > 1:
#        self.call_service("media_player/join", entity_id=self.speakers[0], group_members=self.speakers[1:])
#      
#      # play the chime
#      # self.call_service("media_player/play_media", entity_id=self.speakers[0], media_content_id=media-source://media_source/local/doorbell-223669.mp3, media_content_type=audio/mp3, announce=True)
#      
#      # restore the volumes
#      for speaker,vol in zip(self.speakers, current_volumes):
#        current_volume = self.get_state(entity_id=speaker, attribute='volume_level')
#        self.log(f'Restoring {speaker} from {current_volume} to {vol}')
#        self.call_service("media_player/volume_set", entity_id=speaker, volume_level=vol)
#      
#      # unjoin the speakers if there are more than one
#      if len(self.speakers) > 1:
#        for speaker in self.speakers:
#          self.call_service("media_player/unjoin", entity_id=speaker)
#
#      
#    '''
#    Generic log for state listeners
#    '''
#    def logit(self, entity, old, new):
#      self.log(f"{entity}: Was {old}, changed to {new}.")
#
#    def handle_doorbell(self, entity, attribute, old, new, kwargs):
#        self.logit(entity, old, new)
        

