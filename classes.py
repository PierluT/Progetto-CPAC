import time
import random
import numpy as np
from threading import Thread, Event
from pythonosc import udp_client
from dizionari import scale_per_accordo,chords_midi_dict,basic_grammar,scale_midi_per_accordo
import argparse
from pythonosc import udp_client
from tempo import default_word_dur

ID_START =0
scala_corrente = []
num_note_generate = 0
nota1 = 0
nota2 = 0
nota3 = 0
nota4 = 0
note_generate =[]

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
                                "amplitude: %.1f"%self.amp])
                                #"BPM: %d"%self.BPM
    
    def note_sleep(BPM, beats):
        time.sleep(beats*60./BPM)

    def beats_to_seconds(BPM, beats):
        return beats*60./BPM
    
class Accordo:

     def __init__(self,amp = 1,BPM= 80,nota1 = 0,nota2 = 0,nota3 = 0,sigla = "",durata = 0):
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
    
     def get_sigla(self):
         return self.sigla
     
     def set_durata(self,durata):
         self.durata=durata

class Battuta:
    def __init__(self):
        self.accordo = Accordo()
        self.note = []
        
    def set_accordo(self,accordo):
        self.accordo = accordo
    
    def set_note(self,nota):
        if isinstance(nota,Nota):
            self.note.append(nota)
        else:
            print("Tentativo di aggiungere un oggetto non valido alla lista delle note.")

class Composizione(Nota, Accordo):
        
     def genera_melodia_per_battuta(self,Accordo,numeroNote):
          
          if Accordo.tipologia == "consonanza":
            # regole per successione consonante
            scala_corrente = scale_midi_per_accordo[Accordo.sigla]
            #salto intervallo
            salto_intervallo = 2
            #per la consonanza si può partire dalla prima,dalla quarta nota
            posizione_iniziale = random.choice([0,3])
            nota_iniziale = scala_corrente[posizione_iniziale]
            
            if(numeroNote == 2):
                nota1 = nota_iniziale
                nota2 = scala_corrente[posizione_iniziale + salto_intervallo]
                note_generate = [nota1,nota2]

            if(numeroNote == 3):
                nota1 = nota_iniziale
                nota2 = scala_corrente[posizione_iniziale + salto_intervallo]
                nota3 = scala_corrente[posizione_iniziale + salto_intervallo + 1]
                note_generate =[ nota1,nota2,nota3]

            if(numeroNote == 4):   
                nota1 = nota_iniziale
                nota2 = scala_corrente[posizione_iniziale + salto_intervallo]
                nota3 = scala_corrente[posizione_iniziale + salto_intervallo + 1]
                nota4 = scala_corrente[posizione_iniziale + salto_intervallo + 2]
                note_generate=[nota1,nota2,nota3,nota4]

            return note_generate
          if Accordo.tipologia == "dissonanza":
            # regole per successione dissonanza
            scala_corrente = scale_midi_per_accordo[Accordo.sigla]
            
            #per la dissonanza si può partire dalla seconda,dalla sesta o dalla settima nota
            posizione_iniziale = random.choice([0,3,4])
            nota_iniziale = scala_corrente[posizione_iniziale]

            if(numeroNote == 2):
                nota1 = nota_iniziale
                nota2 = scala_corrente[posizione_iniziale + random.choice([2,3])]
                note_generate = [nota1,nota2]
            if(numeroNote == 3):
                nota1 = nota_iniziale
                nota2 = scala_corrente[posizione_iniziale + random.choice([2,3])]
                nota3 = scala_corrente[posizione_iniziale + random.choice([1,3])]
                note_generate =[ nota1,nota2,nota3]
            if(numeroNote == 4): 
                nota1 = nota_iniziale
                nota2 = scala_corrente[posizione_iniziale + random.choice([1,3])]
                nota3 = scala_corrente[posizione_iniziale + random.choice([1,3])]
                nota4 = scala_corrente[posizione_iniziale + random.choice([1,3])]
                note_generate =[ nota1,nota2,nota3,nota4]
            
            return note_generate

            # Genera una lista dei primi n numero della scala dell'accordo
            #note_generate = scala_corrente[:numeroNote]

          return tuple(note_generate)

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

    