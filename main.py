import numpy as np
import pandas as pd
from collections import Counter
import time
import random
from markov import Markov
from dizionari import scale_midi_per_accordo,chords_midi_dict
from classes import Nota,OscManager,Accordo,Composizione, Battuta
from tempo import Grammar_Sequence, metronome_grammar,default_word_dur,basic_grammar

accordo_iniziale = 'C'
sigla_accordo = ""
risposta = ""
prefisso = "dim"
# variabili 
numero_figure_metriche = []
lunghezza_composizione = 0
sequenza_ritmica_melodia = []
sequenza_ritmica_melodia_divisa = [] 
pos = 0
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

#futuro main
birgrammi_consonanti = markov.calcola_bigrammi_consonanti()
bigrammi_dissonanti = markov.calcola_bigrammi_dissonanti()

while True:

    risposta = input("vuoi continuare a comporre? (y/n):")

    if risposta == 'y':
        lunghezza_composizione +=1
        valore_provvisorio_scelta_accordo = random.randint(0,1)

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
            scala_da_usare = scale_midi_per_accordo[sigla_accordo]
            scale_da_usare.append(scala_da_usare)
        else :
            choosen_chord_sequence = bigrammi_dissonanti
            print("dissonanza")
            sigla_accordo = markov.predict_next_state(accordo_iniziale,choosen_chord_sequence)
            print("questo è l'accordo predetto: "+ sigla_accordo)
            accordo = Accordo()
            accordo.set_tipologia("consonanza")
            accordo.set_sigla(sigla_accordo)
            accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
            sequenza_accordi_per_scale.append(accordo)
            accordo_iniziale = sigla_accordo
    else : break 

# INIZIO COMPOSIZIONE 
START_SEQUENCE=["M",]*lunghezza_composizione
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

# assegno la durata alle note 
for numeri_note,lettere_note in zip(melodia_totale,sequenza_ritmica_melodia_divisa):
    sottosequenza = []
    for numero,lettera in zip(numeri_note,lettere_note):
            durata = default_word_dur.get(lettera, 0)
            nota = Nota()
            nota.midinote = numero
            nota.dur = durata
            sottosequenza.append(nota)
    melodia_definitiva_con_ritmo.append(sottosequenza)

# setto la battuta con l'oggetto Accordo e l'oggetto note 
for accordo,array_note_battuta in zip(sequenza_accordi_per_scale,melodia_definitiva_con_ritmo):
    battuta = Battuta()
    battuta.set_accordo(accordo)
    for a in array_note_battuta:
         #print("sono arrivato qua :"+ str(a.dur))
        battuta.set_note(a)
    totale_battute.append(battuta)


"""
#  ASSEGNO AD OGNI ACCORDO LA DURATA IN BASE ALLA GRAMMAR BASE
for element in sequenza_accordi_per_scale:
    pos_metrica_accordi= 0
     #print("la durata di questo accordo è: "+ str(element.durata))
    element.set_durata(grammar.sequenza_ritmica_accordi(START_SEQUENCE)[pos_metrica_accordi])
    pos_metrica_accordi += 1

for element in sequenza_accordi_per_scale:
     print("la durata di questo accordo è: "+ str(element.durata))

"""


# MESSAGGI OSC MELDIA ED ARMONIA
for battuta in totale_battute:
     #mando_composizione.send_message("/synth_control_accordi",['stop'])
     mando_composizione.send_message("/synth_control_accordi",['chord3',battuta.accordo.nota1,battuta.accordo.nota2,battuta.accordo.nota3])
     for nota in battuta.note:
          print(nota.dur)
          mando_composizione.send_message("/synth_control_melodia",['nota',nota.midinote,nota.dur])
          time.sleep(0.5)

