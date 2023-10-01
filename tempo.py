import random

default_word_dur={"h":0.5, # half-measure
          "q":0.25, # quarter-measure
          "m":1, # semibreve
}
metronome_grammar={
    "M":["q","q","q","q"]
}
basic_grammar={
    "S":["M", "SM"],
    "M": [["H","H"]],    
    "H": ["h", ["q","q"]],
}

def random_elem_in_list(list_of_elems):
    return list_of_elems[random.randint(0,len(list_of_elems)-1)]

class Grammar_Sequence:
    def __init__(self, grammar):
        self.grammar=grammar
        self.grammar_keys=list(grammar.keys())
        self.N=len(self.grammar_keys)
        self.sequence=[]
    def replace(self, index, convert_to):
        """Replace symbol in index with symbol(s) in convert_to

        Parameters
        ----------
        index : int
            index of the sequence to replace
        convert_to : str, list of str
            symbol(s) to convert to
        """
        convert_to = [convert_to,] if type(convert_to)==str else convert_to
        begin_seq=self.sequence[:index]
        end_seq=self.sequence[index+1:] if (index+1)<len(self.sequence) else []
        self.sequence=begin_seq+convert_to+end_seq
    def convert_sequence(self, idxs):        
        """Convert a non-terminal symbol in the sequence

        Parameters
        ----------
        idxs : list of integers
            integers where non-terminal symbols are 
        """

        index=random_elem_in_list(idxs)
        symbol=self.sequence[index]
        convert_to = random_elem_in_list(self.grammar[symbol])
        self.replace(index, convert_to)
        
    def find_nonterminal_symbols(self, sequence):
        """Checks if there are still nonterminal symbols in a sequence
        and where they are

        Parameters
        ----------
        sequence : list of str
            sequence

        Returns
        -------
        list
            list of indices where nonterminal symbols are
        boolean
            True if there are nonterminal symbols
        """
        idxs=[]
        for s, symbol in enumerate(sequence):
            if symbol in self.grammar_keys:
                idxs.append(s) 
        return idxs, len(idxs)>0
    def create_sequence(self, start_sequence):
        """Create a sequence of terminal symbols 
        starting from a sequence of non-terminal symbols.
        While this could be done with recursive function, we use iterative approach

        Parameters
        ----------
        start_sequence : list of str
            the sequence of non-terminal symbols

        Returns
        -------
        list of str
            the final sequence of terminal symbols
        list of list of str
            the history of sequence modification from non-terminal to terminal symbols
        """
        self.sequence=start_sequence
        sequence_transformation=[start_sequence]
        while True:
            idxs, to_convert=self.find_nonterminal_symbols(self.sequence)
            if not to_convert:
                break
            self.convert_sequence(idxs)
            sequence_transformation.append(self.sequence.copy())
        return self.sequence, sequence_transformation
    
    def dividi_sequenza_ritmica_melodia(self,final_sequence):
        sequenza_divisa = []
        battuta = []
        tempo_battuta = 0

        # Calcolo durata nota in base alla grammatica  
        for simbolo in final_sequence:
            durata = default_word_dur.get(simbolo, 0)

            if tempo_battuta + durata > 1:
                sequenza_divisa.append(battuta)
                battuta = []
                tempo_battuta = 0

            battuta.append(simbolo)
            tempo_battuta += durata

        # Assicurati di aggiungere l'ultima battuta alla fine
        sequenza_divisa.append(battuta)

        return sequenza_divisa

    def sequenza_ritmica_accordi(self,START_SEQUENCE):
        sequenza_ritmica_finale_accordi = []
        
        sequenza_ritmica_finale_accordi = ["m" if elemento == "M" else elemento for elemento in START_SEQUENCE ]
        return sequenza_ritmica_finale_accordi
    
    def numero_figurazioni(self,sequenza_ritmica_melodia_divisa):
            numero_figurazioni = []
            for element in sequenza_ritmica_melodia_divisa: 
                #numero note per battuta
                contatore_note = 0
                contatore_note += len(element)
                numero_figurazioni.append(contatore_note)
            
            return numero_figurazioni

    

