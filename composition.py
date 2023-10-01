import numpy as np
import pandas as pd
from collections import Counter
import time
import argparse
import random
import os
from tensorflow.keras.models import load_model
from kapre.time_frequency import STFT, Magnitude, ApplyFilterbank, MagnitudeToDecibel
from markov import Markov
from dizionari import scale_midi_per_accordo,chords_midi_dict
from classes import Nota,OscManager,Accordo,Composizione, Battuta
from tempo import Grammar_Sequence, metronome_grammar,default_word_dur,basic_grammar
import sys
import pathlib
import sounddevice as sd


accordo_iniziale = 'C'
sigla_accordo = ""
risposta = ""
START_SEQUENCE=["M",]*1

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
                #client.send_message('/stick', hittedby)
                #stick.stick = hittedby                
        counter=counter+1
if __name__ == "__main__":

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

    window = np.random.randint(-32768,32768,size=(4800, 1))
    window = np.zeros((4800,1))
    model = load_model(args.model_fn,
        custom_objects={'STFT':STFT,
                        'Magnitude':Magnitude,
                        'ApplyFilterbank':ApplyFilterbank,
                        'MagnitudeToDecibel':MagnitudeToDecibel})
    classes = sorted(os.listdir(args.src_dir))
    counter=0


    while True:

        valore_provvisorio_scelta_accordo = random.randint(0,1)
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

        


        if valore_provvisorio_scelta_accordo == 0 :
            choosen_chord_sequence = birgrammi_consonanti
            print("consonanza")
            # PROBLEMA 'C'
            sigla_accordo = markov.predict_next_state('C',choosen_chord_sequence)
            print("questo è l'accordo predetto: "+ sigla_accordo)
            accordo = Accordo()
            accordo.set_tipologia("consonanza")
            accordo.set_sigla(sigla_accordo)
            accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
            #accordo.set_durata()
            sequenza_accordi_per_scale.append(accordo)
            #accordo_iniziale = sigla_accordo
            #scala_da_usare = scale_midi_per_accordo[sigla_accordo]
            #scale_da_usare.append(scala_da_usare)
        else :
            choosen_chord_sequence = bigrammi_dissonanti
            print("dissonanza")
            # PROBLEMA 'C'
            sigla_accordo = markov.predict_next_state('C',choosen_chord_sequence)
            print("questo è l'accordo predetto: "+ sigla_accordo)
            accordo = Accordo()
            accordo.set_tipologia("dissonanza")
            accordo.set_sigla(sigla_accordo)
            accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
            sequenza_accordi_per_scale.append(accordo)
            accordo_iniziale = sigla_accordo
            #scala_da_usare = scale_midi_per_accordo[sigla_accordo]
            #scale_da_usare.append(scala_da_usare)
            #print(scala_da_usare)

        sequenza_ritmica_melodia,seqs = grammar.create_sequence(START_SEQUENCE)
        sequenza_ritmica_melodia_divisa = grammar.dividi_sequenza_ritmica_melodia(sequenza_ritmica_melodia)

        for element in sequenza_ritmica_melodia_divisa:
            #numero note per battuta
            contatore_note = 0
            contatore_note += len(element)
            print(contatore_note)
            numero_figure_metriche.append(contatore_note)

        for element in sequenza_accordi_per_scale:
            note_battuta = compositore.genera_melodia_per_battuta(element, numero_figure_metriche[pos])
            #print(note_battuta)
            melodia_totale.append(note_battuta)
            pos += 1

        for numeri_note,lettere_note in zip(melodia_totale,sequenza_ritmica_melodia_divisa):
            sottosequenza = []
            for numero,lettera in zip(numeri_note,lettere_note):
                durata = default_word_dur.get(lettera, 0)
                nota = Nota()
                nota.midinote = numero
                nota.dur = durata
                sottosequenza.append(nota)
            melodia_definitiva_con_ritmo.append(sottosequenza)
        
        for accordo,array_note_battuta in zip(sequenza_accordi_per_scale,melodia_definitiva_con_ritmo):
            battuta = Battuta()
            battuta.set_accordo(accordo)
            for a in array_note_battuta:
                #print("sono arrivato qua :"+ str(a.dur))
                battuta.set_note(a)
            totale_battute.append(battuta)

        for battuta in totale_battute:
            print("nota 1: " + str(battuta.accordo.nota1) + " nota 2: " + str(battuta.accordo.nota2) +" nota 3: " +str(battuta.accordo.nota3))
            mando_composizione.send_message("/synth_control_accordi",['chord3',battuta.accordo.nota1,battuta.accordo.nota2,battuta.accordo.nota3])
            for nota in battuta.note:
                print(nota.dur)
                mando_composizione.send_message("/synth_control_melodia",['nota',nota.midinote,nota.dur])
                time.sleep(1)
    