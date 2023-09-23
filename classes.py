import time
import numpy as np
from threading import Thread, Event
from pythonosc import udp_client
from dizionari import scale_per_accordo,chords_midi_dict,basic_grammar
import argparse
from pythonosc import udp_client

ID_START =0

class Nota:

    def __init__(self,id =0,tipologia= "",midinote=0,dur =0,amp =0,BPM=80):
         self.id = ID_START
         self.tipologia = tipologia
         self.midinote=midinote
         self.amp=amp
         self.dur=dur
    
    def __str__(self):
        return "\n\t".join([ 
                                "midinote: %d"%self.midinote, 
                                "duration: %s beats"%str(self.dur),
                                "amplitude: %.1f"%self.amp,
                                "BPM: %d"%self.BPM])
    
    def note_sleep(BPM, beats):
        time.sleep(beats*60./BPM)

    def beats_to_seconds(BPM, beats):
        return beats*60./BPM
    
class Accordo:
     
     def __init__(self,durata = 1,amp = 1,BPM= 80):
          self.durata = durata
          self.amp = amp 

     def set_tipologia(self,tipologia):
         self.tipologia = tipologia

     def set_note(self, nota1, nota2, nota3):
        self.nota1 = nota1
        self.nota2 = nota2
        self.nota3 = nota3  

     def set_sigla(self,sigla):
        self.sigla = sigla
          

"""
class Composizione(Nota):
     def __init__(self, BPM=120):
        Composizione.__init__(self,BPM=BPM)
    
     def net(self):
          if self.tipologia == "consonanza":
            # regole per successione consonante
        
          if self.tipologia == "dissonanza":
            # regole per successione dissonanza
"""            

class OscManager:

    def start_osc_communication_melodia(self):
            # argparse helps writing user-friendly commandline interfaces
            parser = argparse.ArgumentParser()
            parser.add_argument("--ip", default='127.0.0.1', help="The ip of the OSC server")
            # OSC server port (check on SuperCollider)
            parser.add_argument("--port", type=int, default=57120, help="The port the OSC server is listening on")
            
            # Parse the arguments
            args = parser.parse_args()

            # Start the UDP Client
            client = udp_client.SimpleUDPClient(args.ip, args.port)

            return client
        
    def start_osc_communication_accordi(self):
        # argparse helps writing user-friendly commandline interfaces
        parser = argparse.ArgumentParser()
        # OSC server ip
        parser.add_argument("--ip", default='127.0.0.1', help="The ip of the OSC server")
        # OSC server port (check on SuperCollider)
        parser.add_argument("--port", type=int, default=57120, help="The port the OSC server is listening on")

        # Parse the arguments
        args = parser.parse_args()

        # Start the UDP Client
        client = udp_client.SimpleUDPClient(args.ip, args.port)

        return client
    
 
"""   
    def __init__(self, accordi_port=57121, melodia_port=57120):
        self.accordi_client = self._start_osc_communication(accordi_port)
        self.melodia_client = self._start_osc_communication(melodia_port)

    def _start_osc_communication(self, port):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default='127.0.0.1', help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=port, help="The port the OSC server is listening on")
        
        args = parser.parse_args()

        client = udp_client.SimpleUDPClient(args.ip, args.port)

        return client

    def send_accordo_message(self, message):
        self.accordi_client.send_message("/accordi", message)

    def send_melodia_message(self, message):
        self.melodia_client.send_message("/melodia", message)

"""






