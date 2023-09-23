import numpy as np
import pandas as pd
from collections import Counter
import time
import argparse
import random
from dizionari import scale_midi_per_accordo,chords_midi_dict
from classes import Nota,OscManager,Accordo

accordo_iniziale = 'C'
sigla_accordo = ""
risposta = ""
choosen_chord_sequence = []
count = 0
# create list to store future chords
chords = []
scala_da_usare = []
sequenza_accordi_per_scale = []
melodia_totale = []
#osc_manager = OscManager(accordi_port=57120, melodia_port=57121)
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
        count +1
        valore_provvisorio_scelta_accordo = random.randint(0,1)

        if valore_provvisorio_scelta_accordo == 0 :
            choosen_chord_sequence = consonant_bigrams
            """
            sigla_accordo = predict_next_state('C',choosen_chord_sequence)
            # GENERATE THE SEQUENCE
            print("questo è l'accordo predetto: "+ sigla_accordo)
            chords = generate_sequence(sigla_accordo)
            print(chords)
            """
            sigla_accordo = predict_next_state(accordo_iniziale,choosen_chord_sequence)
            print("questo è l'accordo predetto: "+ sigla_accordo)
            accordo = Accordo()
            accordo.set_tipologia("consonanza")
            accordo.set_sigla(sigla_accordo)
            accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
            sequenza_accordi_per_scale.append(accordo)
            accordo_iniziale= sigla_accordo
            scala_da_usare = scale_midi_per_accordo[sigla_accordo]
            #sequenza_accordi_per_scale.append(sigla_accordo)
                
            for b in scala_da_usare:
                    note = Nota()
                    note.tiplogia = "consonanza"
                    note.midinote = b
                    note.amp = 0.2
                    note.dur = 0.5
                    melodia_totale.append(note)
           
        else :
            choosen_chord_sequence = dissonant_bigrams
            sigla_accordo = predict_next_state('C',choosen_chord_sequence)
            """
            # GENERATE THE SEQUENCE
            print("questo è l'accordo predetto: "+ sigla_accordo)
            chords = generate_sequence(sigla_accordo)
            print(chords)
            """
            sigla_accordo = predict_next_state(accordo_iniziale,choosen_chord_sequence)
            print("questo è l'accordo predetto: "+ sigla_accordo)
            accordo = Accordo()
            accordo.set_tipologia("consonanza")
            accordo.set_sigla(sigla_accordo)
            accordo.set_note(chords_midi_dict[sigla_accordo][0],chords_midi_dict[sigla_accordo][1],chords_midi_dict[sigla_accordo][2])
            sequenza_accordi_per_scale.append(accordo)
            accordo_iniziale= sigla_accordo
            scala_da_usare = scale_midi_per_accordo[sigla_accordo]
                #print(scala_da_usare)
            for b in scala_da_usare:
                    note = Nota()
                    note.id = "dissonanza"
                    note.midinote = b
                    note.amp = 0.2
                    note.dur = 0.5
                    melodia_totale.append(note)    
    else : break 

#print('Play the sequence with supercollider:')

#send melodia
for element in melodia_totale:
            mando_nota.send_message("/synth_control_melodia",[element.midinote,element.amp,element.dur])
            time.sleep(1)

# Send chords
for c in sequenza_accordi_per_scale:
        print("nota 1: " + str(c.nota1) + " nota 2: " + str(c.nota2) +" nota 3: " +str(c.nota3) )
        #osc_manager.send_accordo_message(['chord3',chords_midi_dict[c][0],chords_midi_dict[c][1],chords_midi_dict[c][2]])
        mando_accordo.send_message("/synth_control_accordi",['chord3',c.nota1,c.nota2,c.nota3])
        time.sleep(1)

