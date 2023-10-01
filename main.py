import numpy as np
import pandas as pd
from collections import Counter
import time
import random
from markov import Markov
from dizionari import scale_midi_per_accordo,chords_midi_dict
from classes import Nota,OscManager,Accordo,Composizione, Battuta,MelodiaProcessor,BattuteProcessor
from tempo import Grammar_Sequence,default_word_dur,basic_grammar
from tensorflow.keras.models import load_model
from kapre.time_frequency import STFT, Magnitude, ApplyFilterbank, MagnitudeToDecibel
import argparse
import os
import sounddevice as sd
from pythonosc import udp_client
import stick


accordo_iniziale = 'D'
sigla_accordo = ""
numero_ricevuto = 2
# variabili 
#numero_figure_metriche = []
lunghezza_composizione = 1
sequenza_ritmica_melodia = []
sequenza_ritmica_melodia_divisa = [] 
pos = 0
colpo_bacchetta = False
#variabile temporanea per note di quell'accordo
scala_da_usare = []
#array della successione degli accordi
sequenza_accordi_per_scale = []
#variabile temporanea scale totali
scale_da_usare = []
#array delle note totali per la melodia
melodia_totale = []
melodia_definitiva_con_ritmo = []
totale_battute = []

# INIZIALIZZAZIONE VARIABILE OSC
client_compositore = OscManager()
mando_composizione = client_compositore.start_osc_communication()

# INIZIALIZZAZIONE OGGETTI
compositore = Composizione()
grammar = Grammar_Sequence(basic_grammar)
markov = Markov()

birgrammi_consonanti = markov.calcola_bigrammi_consonanti()
bigrammi_dissonanti = markov.calcola_bigrammi_dissonanti()

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text
    
def callback(indata, frames, time, status):
    global window, model, classes, counter
    screening_window = np.array((2,2))
    if any(indata):
        window=window[indata.shape[0]:window.shape[0],:]   
        window=np.concatenate((window, indata), axis=0)
        x = np.expand_dims(window, axis=0)
        #each 5 updates make and print prediction
        if (counter%10)==0:
            if np.max(x)>300:            
                #mask, env = envelope(x[0,:,0], args.sr, threshold=args.threshold)
                #x = x[0,mask,0]
                yhat = model.predict(x)
                hittedby = np.argmax(yhat)  # 0 = heart , 1 = irregular, 2 = sphere
                hittedby = int(hittedby)
                #yhat = np.argmax(yhat)
                print(classes[np.argmax(yhat)], yhat)
                client.send_message('/stick', hittedby)
                stick.stick = hittedby                
        counter=counter+1

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Audio Classification Prediction')
    parser.add_argument('--model_fn', type=str, default='audioclassification/models/conv2d.h5',
                        help='model file to make predictions')
    parser.add_argument('--src_dir', type=str, default='audioclassification/wavfiles',
                        help='directory containing wavfiles to predict')
    parser.add_argument('-d', '--device', type=int_or_str,
                        help='input device (numeric ID or substring)')
    parser.add_argument('--sr', type=int, default=16000,
                        help='sample rate of clean audio')
    parser.add_argument('--threshold', type=str, default=20,
                        help='threshold magnitude for np.int16 dtype')
    args, _ = parser.parse_known_args()

    #inizialize osc client
    client = udp_client.SimpleUDPClient("192.168.178.106", 12345)
    


    window = np.random.randint(-32768,32768,size=(4800, 1))
    window = np.zeros((4800,1))
    model = load_model(args.model_fn,
        custom_objects={'STFT':STFT,
                        'Magnitude':Magnitude,
                        'ApplyFilterbank':ApplyFilterbank,
                        'MagnitudeToDecibel':MagnitudeToDecibel})
    classes = sorted(os.listdir(args.src_dir))
    counter=0

    stream = sd.InputStream(device=args.device, channels=1, callback=callback, blocksize=480,
                           samplerate=args.sr,
                           dtype= np.int16)
    
    #print(stick.stick)
    stick.initialize()
    currentstick=stick.stick

    # GENERAZIONE TRAMITE BACCHETTA
    with stream:
        while True:

            sigla_accordo = ""
            risposta = ""
            numero_figure_metriche = []
            lunghezza_composizione = 0
            sequenza_ritmica_melodia = []
            sequenza_ritmica_melodia_divisa = [] 
            pos = 0
            scala_da_usare = []
            sequenza_accordi_per_scale = []
            scale_da_usare = []
            melodia_totale = []
            melodia_definitiva_con_ritmo = []
            totale_battute = []
            if currentstick!=stick.stick:
                currentstick=stick.stick
                print(currentstick)

            #lunghezza_composizione +=1
            valore_provvisorio_scelta_accordo = currentstick
            if valore_provvisorio_scelta_accordo == 0 :
                choosen_chord_sequence = birgrammi_consonanti
                print("consonanza")   
                sigla_accordo = markov.predict_next_state(accordo_iniziale,choosen_chord_sequence)
                print("questo è l'accordo predetto: "+ sigla_accordo)
                accordo = Accordo()
                accordo.set_tipologia("consonanza")
                accordo.set_sigla(sigla_accordo)
                accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
                sequenza_accordi_per_scale.append(accordo)
                accordo_iniziale = sigla_accordo
            elif valore_provvisorio_scelta_accordo == 1: 
                choosen_chord_sequence = bigrammi_dissonanti
                print("dissonanza")
                sigla_accordo = markov.predict_next_state(accordo_iniziale,choosen_chord_sequence)
                print("questo è l'accordo predetto: "+ sigla_accordo)
                accordo = Accordo()
                accordo.set_tipologia("dissonanza")
                accordo.set_sigla(sigla_accordo)
                accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
                sequenza_accordi_per_scale.append(accordo)
                accordo_iniziale = sigla_accordo
                
            # INIZIO COMPOSIZIONE 
            START_SEQUENCE=["M",]
            sequenza_ritmica_melodia,seqs = grammar.create_sequence(START_SEQUENCE)
            sequenza_ritmica_melodia_divisa = grammar.dividi_sequenza_ritmica_melodia(sequenza_ritmica_melodia)
            numero_figure_metriche = grammar.numero_figurazioni(sequenza_ritmica_melodia_divisa)
            for element in sequenza_accordi_per_scale:
                note_battuta = compositore.genera_melodia_per_battuta(element, numero_figure_metriche[pos])
                #print(note_battuta)
                melodia_totale.append(note_battuta)
                pos += 1
            # in questo punto conosco melodia totale e sequenza ritmica divisa
            melodia_processor = MelodiaProcessor(melodia_totale,sequenza_ritmica_melodia_divisa)
            melodia_definitiva_con_ritmo= melodia_processor.processa_melodia()
            composizione_totale = BattuteProcessor()
            totale_battute = composizione_totale.elabora_melodia(sequenza_accordi_per_scale,melodia_definitiva_con_ritmo)
            
            #print(totale_battute.battuta.accordo)
            
            # MESSAGGI OSC MELDIA ED ARMONIA
            for battuta in totale_battute:
                print(battuta.accordo.nota1)
                #mando_composizione.send_message("/synth_control_accordi",['stop'])
                mando_composizione.send_message("/synth_control_accordi",['chord3',battuta.accordo.nota1,battuta.accordo.nota2,battuta.accordo.nota3])
                for nota in battuta.note:
                    print(nota.dur)
                    mando_composizione.send_message("/synth_control_melodia",['nota',nota.midinote,nota.dur])
                    time.sleep(0.5)

