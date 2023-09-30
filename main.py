import numpy as np
import pandas as pd
from collections import Counter
import time
import random
import keyboard
from markov import Markov
from dizionari import scale_midi_per_accordo,chords_midi_dict
from classes import Nota,OscManager,Accordo,Composizione, Battuta,MelodiaProcessor,BattuteProcessor
from tempo import Grammar_Sequence,default_word_dur,basic_grammar

accordo_iniziale = 'C'
sigla_accordo = ""
risposta = ""
# variabili 
#numero_figure_metriche = []
lunghezza_composizione = 0
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

if __name__=="__main__":

 # GENERO MELODIA CONTINUA CONSONANTE
    while not colpo_bacchetta:
        count = 0
        lunghezza_composizione_continua = 4
        sigla_accordo_iniziale_continuo = 'C'
        sequenza_accordi_consonanti_continui = []
        melodia_totale_continua = []
        START_SEQUENCE_CONTINUA=["M",]*lunghezza_composizione_continua
        sequenza_ritmica_melodia_continua,seqs = grammar.create_sequence(START_SEQUENCE_CONTINUA)
        sequenza_ritmica_melodia_continua_divisa = grammar.dividi_sequenza_ritmica_melodia(sequenza_ritmica_melodia_continua)

        for i in range(lunghezza_composizione_continua):
            sigla_accordo = markov.predict_next_state(sigla_accordo_iniziale_continuo,birgrammi_consonanti)
            accordo = Accordo()
            accordo.set_tipologia("consonanza")
            accordo.set_sigla(sigla_accordo)
            accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
            sequenza_accordi_consonanti_continui.append(accordo)
            sigla_accordo_iniziale_continuo = sigla_accordo

        print(sequenza_accordi_consonanti_continui)
        numero_figure_metriche_continue = grammar.numero_figurazioni(sequenza_ritmica_melodia_continua_divisa)
        print(numero_figure_metriche_continue)
        
        for element in sequenza_accordi_consonanti_continui:
            note_battuta = compositore.genera_melodia_per_battuta(element, numero_figure_metriche_continue[count])
            #print(note_battuta)
            melodia_totale_continua.append(note_battuta)
            count += 1
        # in questo punto conosco melodia totale e sequenza ritmica divisa
        melodia_processor_continua = MelodiaProcessor(melodia_totale_continua,sequenza_ritmica_melodia_continua_divisa)
        melodia_definitiva_continua_con_ritmo= melodia_processor_continua.processa_melodia()

        composizione_totale_continua = BattuteProcessor()
        totale_battute_continue = composizione_totale_continua.elabora_melodia(sequenza_accordi_consonanti_continui,melodia_definitiva_continua_con_ritmo)

        # MESSAGGI OSC MELDIA ED ARMONIA
        for battuta in totale_battute_continue:
            #mando_composizione.send_message("/synth_control_accordi",['stop'])
            mando_composizione.send_message("/synth_control_accordi",['chord3',battuta.accordo.nota1,battuta.accordo.nota2,battuta.accordo.nota3])
            for nota in battuta.note:
                print(nota.dur)
                mando_composizione.send_message("/synth_control_melodia",['nota',nota.midinote,nota.dur])
                time.sleep(0.5)
        colpo_bacchetta = True

# GENERAZIONE TRAMITE BACCHETTA
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



# MESSAGGI OSC MELDIA ED ARMONIA
for battuta in totale_battute:
     #mando_composizione.send_message("/synth_control_accordi",['stop'])
     mando_composizione.send_message("/synth_control_accordi",['chord3',battuta.accordo.nota1,battuta.accordo.nota2,battuta.accordo.nota3])
     for nota in battuta.note:
          print(nota.dur)
          mando_composizione.send_message("/synth_control_melodia",['nota',nota.midinote,nota.dur])
          time.sleep(0.5)

