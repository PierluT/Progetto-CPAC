import numpy as np
import pandas as pd
from collections import Counter
import time
import argparse
import random
from dizionari import scale_midi_per_accordo,chords_midi_dict
from classes import Nota,OscManager,Accordo,Composizione, Battuta
from tempo import Grammar_Sequence, metronome_grammar,default_word_dur,basic_grammar

accordo_iniziale = 'C'
sigla_accordo = ""
risposta = ""
choosen_chord_sequence = []
compositore = Composizione()
numero_figure_metriche = []
grammar = Grammar_Sequence(basic_grammar)
lunghezza_composizione = 0
sequenza_ritmica_melodia = []
sequenza_ritmica_melodia_divisa = []
pos = 0
# create list to store future chords
chords = []
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

# INIZIALIZZAZIONE VARIABILI OSC
client_melodia = OscManager()
client_accordi = OscManager()
mando_accordo = client_accordi.start_osc_communication_accordi()
mando_nota = client_melodia.start_osc_communication_melodia()

#Read consonant Chord Collection file
data_consonant_chords = pd.read_csv("C:\\Users\\pierl\\Desktop\\MMI\\CPAC\\cpac_course_2022\\labs\\Progetto\\data\\consonant_chords.csv")
data_consonant_chords

# Generate Bigrams
n = 2
consonant_chords = data_consonant_chords['chords'].values
ngrams = zip(*[consonant_chords[i:] for i in range(n)])
consonant_bigrams = [" ".join(ngram) for ngram in ngrams]
consonant_bigrams[:5]

#Read dissonant Chord Collection file
data_dissonant_chords = pd.read_csv("C:\\Users\\pierl\\Desktop\\MMI\\CPAC\\cpac_course_2022\\labs\\Progetto\\data\\dissonant_chords.csv")
data_dissonant_chords

# Generate Bigrams

dissonant_chords = data_dissonant_chords['chords'].values

ngrams = zip(*[dissonant_chords[i:] for i in range(n)])
dissonant_bigrams = [" ".join(ngram) for ngram in ngrams]
dissonant_bigrams[:5]

def predict_next_state(chord:str, data:list=choosen_chord_sequence):
    #Predict next chord based on current state

    # create list of bigrams which starts with current chord
    bigrams_with_current_chord = [bigram for bigram in choosen_chord_sequence if bigram.split(' ')[0]== chord] 
    # count appearance of each bigram
    #counter counts how many times elements appears in a list
    #dict does a dictionary
    count_appearance = dict(Counter(bigrams_with_current_chord))

    # convert appearance into probabilities
    for ngram in count_appearance.keys():
        #now we divide count_apparence of the current bigram / by the length of the bigrams
        count_appearance[ngram] = count_appearance[ngram]/ len(bigrams_with_current_chord)
    # create list of possible options for the next chord
    # options are given by key
    options = [key.split(' ')[1] for key in count_appearance.keys()]
    # create  list of probability distribution
    probabilities = list(count_appearance.values())
    # return random prediction
    return np.random.choice(options, p= probabilities)

def generate_sequence(chord:str=None, data:list=choosen_chord_sequence, length:int=1):
    """Generate sequence of defined length."""
    # create list to store future chords
    for n in range(length):
        # append next chord for the list
        chords.append(predict_next_state(chord))
        # use last chord in sequence to predict next chord
        chord = chords[-1]
    return chords  

#futuro main
while True:
    risposta = input("vuoi continuare a comporre? (y/n):")

    if risposta == 'y':
        lunghezza_composizione +=1
        valore_provvisorio_scelta_accordo = random.randint(0,1)

        if valore_provvisorio_scelta_accordo == 0 :
            choosen_chord_sequence = consonant_bigrams
            print("consonanza")
            # PROBLEMA 'C'
            sigla_accordo = predict_next_state('C',choosen_chord_sequence)
            print("questo è l'accordo predetto: "+ sigla_accordo)
            accordo = Accordo()
            accordo.set_tipologia("consonanza")
            accordo.set_sigla(sigla_accordo)
            accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
            #accordo.set_durata()
            sequenza_accordi_per_scale.append(accordo)
            #accordo_iniziale = sigla_accordo
            scala_da_usare = scale_midi_per_accordo[sigla_accordo]
            #sequenza_accordi_per_scale.append(sigla_accordo)
            scale_da_usare.append(scala_da_usare)
        else :
            choosen_chord_sequence = dissonant_bigrams
            print("dissonanza")
             # PROBLEMA 'C'
            sigla_accordo = predict_next_state('C',choosen_chord_sequence)
            print("questo è l'accordo predetto: "+ sigla_accordo)
            accordo = Accordo()
            accordo.set_tipologia("consonanza")
            accordo.set_sigla(sigla_accordo)
            accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
            sequenza_accordi_per_scale.append(accordo)
            accordo_iniziale = sigla_accordo
            scala_da_usare = scale_midi_per_accordo[sigla_accordo]
            scale_da_usare.append(scala_da_usare)
            #print(scala_da_usare)
    else : break 

# INIZIO COMPOSIZIONE 

START_SEQUENCE=["M",]*lunghezza_composizione
sequenza_ritmica_melodia,seqs = grammar.create_sequence(START_SEQUENCE)

#print("sto stampando sequenza ritmica melodia")
#print(sequenza_ritmica_melodia)
sequenza_ritmica_melodia_divisa = grammar.dividi_sequenza_ritmica_melodia(sequenza_ritmica_melodia)
#print(sequenza_ritmica_melodia_divisa)

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
#print(melodia_totale)

# ASSEGNO LA DURATA ALLE NOte GENERATE 
for numeri_note,lettere_note in zip(melodia_totale,sequenza_ritmica_melodia_divisa):
    sottosequenza = []
    for numero,lettera in zip(numeri_note,lettere_note):
            durata = default_word_dur.get(lettera, 0)
            nota = Nota()
            nota.midinote = numero
            nota.dur = durata
            sottosequenza.append(nota)
    melodia_definitiva_con_ritmo.append(sottosequenza)

"""
for minilista in melodia_definitiva_con_ritmo:
     for oggetto in minilista:
        print("nota midi: "+ str(oggetto.midinote))
"""

for accordo,array_note_battuta in zip(sequenza_accordi_per_scale,melodia_definitiva_con_ritmo):
    battuta = Battuta()
    battuta.set_accordo(accordo)
    for a in array_note_battuta:
         #print("sono arrivato qua :"+ str(a.dur))
        battuta.set_note(a)
    totale_battute.append(battuta)

# STAMPE DI CONTROLLO 
"""
for element in melodia_definitiva_con_ritmo:
    for b in element:
         print("nota midi : "+b.midinote)
"""
#print("sto stampando melodia definitiva con ritmo")
#print(sequenza_accordi_per_scale)
#print("sto per stampare melodia definitiva con ritmo: ")
#print(melodia_definitiva_con_ritmo)
#print("lunghezza composizione : "+ str(lunghezza_composizione))
#print(grammar.sequenza_ritmica_accordi(START_SEQUENCE))
#print(len(sequenza_accordi_per_scale))
#print("sto per stampare melodia definitiva con ritmo: ")
#print(melodia_definitiva_con_ritmo)
"""
#  ASSEGNO AD OGNI ACCORDO LA DURATA IN BASE ALLA GRAMMAR BASE
for element in sequenza_accordi_per_scale:
    pos_metrica_accordi= 0
     #print("la durata di questo accordo è: "+ str(element.durata))
    element.set_durata(grammar.sequenza_ritmica_accordi(START_SEQUENCE)[pos_metrica_accordi])
    pos_metrica_accordi += 1

for element in sequenza_accordi_per_scale:
     print("la durata di questo accordo è: "+ str(element.durata))

print('Play the sequence with supercollider:')

"""
"""
# SEND ACCORDI E MELODIA
for c in sequenza_accordi_per_scale:
        print("nota 1: " + str(c.nota1) + " nota 2: " + str(c.nota2) +" nota 3: " +str(c.nota3))
        #osc_manager.send_accordo_message(['chord3',chords_midi_dict[c][0],chords_midi_dict[c][1],chords_midi_dict[c][2]])
        mando_accordo.send_message("/synth_control_accordi",['chord3',c.nota1,c.nota2,c.nota3,c.durata])
        posizione = 0
        time.sleep(1)
        for nota in melodia_definitiva_con_ritmo:
                #print(scale_midi_per_accordo[c.sigla][posizione])
            mando_nota.send_message("/synth_control_melodia",[nota.midinote,nota.dur])
            #print(nota.midinote,nota.dur)
                #posizione +=1
            time.sleep(1)
"""

#QUA MANDAVO IL VALORE MIDI PRESO DAL DIZIONARIO PER FARE DELLE PROVE
"""
for nota in scale_midi_per_accordo[c.sigla]:
            print(scale_midi_per_accordo[c.sigla][posizione])
            mando_nota.send_message("/synth_control_melodia",[scale_midi_per_accordo[c.sigla][posizione],])
            posizione +=1
            time.sleep(1)
"""

for battuta in totale_battute:
     print("nota 1: " + str(battuta.accordo.nota1) + " nota 2: " + str(battuta.accordo.nota2) +" nota 3: " +str(battuta.accordo.nota3))
     mando_accordo.send_message("/synth_control_accordi",['chord3',battuta.accordo.nota1,battuta.accordo.nota2,battuta.accordo.nota3])
     for nota in battuta.note:
          print(nota.midinote)
          mando_nota.send_message("/synth_control_melodia",[nota.midinote,nota.dur])
          time.sleep(1)

mando_nota.send_message("/quit",0)