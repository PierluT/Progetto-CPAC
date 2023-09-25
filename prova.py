import numpy as np
import pandas as pd
from collections import Counter
import time
import argparse
from pythonosc import udp_client,osc_message_builder
import random
from dizionari import scale_per_accordo

chords_midi_dict={
    'C':[0,4,7],
    'Cm':[0,3,7],
    'Cdim':[0,3,6],
    'Db':[1,5,8],
    'Dbm':[1,4,8],
    'Dbdim':[1,4,7],
    'D':[2,6,9],
    'Dm':[2,5,9],
    'Ddim':[2,4,9],
    'Eb':[3,7,10],
    'Ebm':[3,6,10],
    'Ebdim':[3,6,9],
    'E':[4,8,11],
    'Em':[4,7,11],
    'Edim':[4,7,10],
    'F':[5,9,12],
    'Fm':[5,8,12],
    'Fdim':[5,8,11],
    'F#':[6,10,13],
    'F#m':[6,9,13],
    'F#dim':[6,9,12],
    'G':[7,11,14], 
    'Gm':[7,10,14],
    'Gdim':[7,10,13],
    'Ab':[8,12,15],
    'Abm':[8,11,15],
    'Abdim':[8,1,14],
    'A':[9,13,16], 
    'Am':[9,12,16],
    'Adim':[9,12,15],
    'Bb':[10,14,17],
    'Bbm':[10,13,17],
    'Bbdim':[10,13,16],
    'B':[11,15,18],
    'Bm':[11,14,18],
    'Bdim':[11,14,17],

    }

risposta = ""
choosen_chord_sequence = []
count = 0
# create list to store future chords
chords = []
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

    for n in range(length):
        # append next chord for the list
        chords.append(predict_next_state(chord))
        # use last chord in sequence to predict next chord
        chord = chords[-1]
    return chords  


while True:
    risposta = input("vuoi continuare a comporre? (y/n):")

    if risposta == 'y':
        count +1
        valore_provvisorio_scelta_accordo = random.randint(0,1)
        if valore_provvisorio_scelta_accordo == 0 :
            choosen_chord_sequence = consonant_bigrams
            result = predict_next_state('C',choosen_chord_sequence)
            print(result)
            # GENERATE THE SEQUENCE
            chords = generate_sequence('C')
        else :
            choosen_chord_sequence = dissonant_bigrams
            result = predict_next_state('C',choosen_chord_sequence)
            print(result)
             # GENERATE THE SEQUENCE
            chords = generate_sequence('C')
    
    else : break 

print('')
print('')
print('Generated Chords Sequence:')
print(chords)
time.sleep(2)
print('')
print('')
print('')
print('Play the sequence with supercollider:')

def start_osc_communication_accordi():
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

def start_osc_communication_melodia():
    # argparse helps writing user-friendly commandline interfaces
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default='127.0.0.1', help="The ip of the OSC server")
    # OSC server port (check on SuperCollider)
    parser.add_argument("--port", type=int, default=57121, help="The port the OSC server is listening on")
    
    # Parse the arguments
    args = parser.parse_args()

    # Start the UDP Client
    client = udp_client.SimpleUDPClient(args.ip, args.port)

    return client


client_accordi = start_osc_communication_accordi()
client_melodia = start_osc_communication_melodia()
    
# Send chords
for c in chords:
    print(c)
    if len(chords_midi_dict[c]) == 3:
        client_accordi.send_message("/synth_control_accordi",['chord3',chords_midi_dict[c][0],chords_midi_dict[c][1],chords_midi_dict[c][2]])
        time.sleep(1)
    if len(c) == 4:
        client_accordi.send_message("/synth_control_accordi",['chord4',chords_midi_dict[c][0],chords_midi_dict[c][1],chords_midi_dict[c][2],chords_midi_dict[c][3]])
        time.sleep(1)





