import numpy as np
import pandas as pd
from collections import Counter
from pathlib import Path

chords = []

class Markov:
    def __init__(self):
        self.choosen_chord_sequence = []  # Inizializza la lista vuota
        self.probabilities_matrix_consonant = []
        self.probabilities_matrix_dissonant = []

    def calcola_bigrammi_consonanti(self):
            #Read consonant Chord Collection file
            data_consonant_chords = pd.read_csv("C:\\Users\\pierl\\Desktop\\MMI\\CPAC\\cpac_course_2022\\labs\\Progetto\\data\\sequenza.c.csv")
            data_consonant_chords

            # Generate Bigrams
            n = 2
            consonant_chords = data_consonant_chords['chords'].values
            ngrams = zip(*[consonant_chords[i:] for i in range(n)])
            consonant_bigrams = [" ".join(ngram) for ngram in ngrams]
            consonant_bigrams[:5]

            return consonant_bigrams
    
    def calcola_bigrammi_dissonanti(self):
            #Read dissonant Chord Collection file
            data_dissonant_chords = pd.read_csv("C:\\Users\\pierl\\Desktop\\MMI\\CPAC\\cpac_course_2022\\labs\\Progetto\\data\\sequenza.d.csv")
            data_dissonant_chords

            # Generate Bigrams
            n = 2
            dissonant_chords = data_dissonant_chords['chords'].values
            ngrams = zip(*[dissonant_chords[i:] for i in range(n)])
            dissonant_bigrams = [" ".join(ngram) for ngram in ngrams]
            dissonant_bigrams[:5]

            return  dissonant_bigrams
    
    def initialize_matrix(self, data_consonant:list = None, data_dissonant: list = None):
         
         #da finire

         bigrams_consonant_appearance = dict(Counter(data_consonant))
         bigrams_dissonant_appearance = dict(Counter(data_dissonant))
         # convert appearance into probabilities
         for ngram in bigrams_consonant_appearance.keys():
            #now we divide count_apparence of the current bigram / by the length of the bigrams
            n_bigram_with_same_initial_chord = len([bigram for bigram in bigrams_consonant_appearance.keys if bigram.split(' ')[0]==ngram.split(' ')[0]])
            bigrams_consonant_appearance[ngram] = bigrams_consonant_appearance[ngram]/ n_bigram_with_same_initial_chord

         for ngram in bigrams_dissonant_appearance.keys():
            #now we divide count_apparence of the current bigram / by the length of the bigrams
            n_bigram_with_same_initial_chord = len([bigram for bigram in bigrams_dissonant_appearance.keys if bigram.split(' ')[0]==ngram.split(' ')[0]])
            bigrams_dissonant_appearance[ngram] = bigrams_dissonant_appearance[ngram]/ n_bigram_with_same_initial_chord
        
         # create list of possible options for the next chord
         # options are given by key
         options = [key.split(' ')[1] for key in bigrams_consonant_appearance.keys()]
         # create  list of probability distribution
         probabilities = list(bigrams_consonant_appearance.values())




         return
         
    

    def predict_next_state(self,chord:str, data:list= None):
        #Predict next chord based on current state

        # create list of bigrams which starts with current chord
        bigrams_with_current_chord = [bigram for bigram in data if bigram.split(' ')[0]== chord] 
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
"""
    def generate_sequence(chord:str=None, data:list=choosen_chord_sequence, length:int=1):
        #Generate sequence of defined length.
        # create list to store future chords
        for n in range(length):
            # append next chord for the list
            chords.append(predict_next_state(chord))
            # use last chord in sequence to predict next chord
            chord = chords[-1]
        return chords  
"""

if __name__=='__main__':
     x = Markov()
     print(x.calcola_bigrammi_consonanti())