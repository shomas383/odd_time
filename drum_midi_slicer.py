import sys
import os
import note_seq
import miditoolkit
from note_seq import NoteSequence
import pretty_midi

def midi_slicer():
    args = sys.argv[1:]
    file = args[0]
    generated_path = args[1]
    #Load to note_seq to check the qpm
    note_seq_sample = note_seq.midi_file_to_note_sequence(file)
    tempo = note_seq_sample.tempos[0].qpm
    i = 0 #define variable to store current index
    #Load via pretty_midi
    cr_bar = 1
    pm = pretty_midi.PrettyMIDI(file)
    end_time = pm.get_end_time()
    delta_time = len(pm.time_signature_changes)
    delta_array = [change.time for change in pm.time_signature_changes]
    delta_array.append(end_time)
    #get the bar_time, takes in pretty midi object
    bar_time = get_bar_to_time_dict(pm)
    current_t = bar_time.get(cr_bar)
    bar_interval = 0
    # Will create slicing_midi for each time sig. change
    for slice in pm.time_signature_changes:
        while current_t < delta_array[i+1]:   
            current_t = bar_time.get(cr_bar)
            next_bar = cr_bar+bar_interval
            next_t = bar_time.get(next_bar)
            bar_interval = 0
            new_pm = pretty_midi.PrettyMIDI(initial_tempo=tempo) #create empty pretty object, assume fixed tempo
            ts = pretty_midi.TimeSignature(slice.numerator,slice.denominator,0)
            new_pm.time_signature_changes.append(ts)
            if slice.numerator == 4 and slice.denominator == 4: #if it's 4/4 time sig
                bar_interval = 3 #cause we use 0 as first bar, plus 3 to get 4 bars
            else:
                bar_interval = 1 #same thing, but we want 2 bars
            #loop through the original midi to retrieve all the instruments(channels) and apply it to new_pm
            current_time = slice.time
            for inst in pm.instruments:
                prog = inst.program
                is_d = inst.is_drum
                na = inst.name
                instrument = pretty_midi.Instrument(program=prog,is_drum=is_d,name=na) #create empty instruments
                new_pm.instruments.append(instrument)
            for inst,new_inst in zip(pm.instruments,new_pm.instruments):
                #extract only the drum part
                if inst.is_drum == True and new_inst.is_drum == True:
                    for notes in inst.notes: #This is the original notes that we want to copy to another object
                        current_t = bar_time.get(cr_bar)
                        next_t = bar_time.get(cr_bar+bar_interval)
                        if notes.start >= current_t and notes.end <= next_t:
                            notes.start = notes.start - current_time
                            notes.end = notes.end - current_time
                            new_inst.notes.append(notes)
            name = str(slice.numerator)+ "_" + str(slice.denominator) + "_" + str(current_t) + ".mid"
            print("Writing out")
            midi_path = os.path.join(generated_path,name)
            new_pm.write(midi_path)
            print("Writing done")
            cr_bar = next_bar
        #i+= 1
        #print(i)

def get_bar_to_time_dict(pm):
    def get_numerator_for_sig_change(signature_change):
        if int(signature_change.numerator)==6 and int(signature_change.denominator)==8:
            # 6/8 goes to 2 for sure
            return 2
        return signature_change.numerator
    changes = pm.time_signature_changes
    beats = pm.get_beats()
    bar_to_time_dict = dict()
    # first bar is on first position
    current_beat_index = 0
    current_bar = 1
    bar_to_time_dict[current_bar] = beats[current_beat_index]
    for index_time_sig, _ in enumerate(changes):
            numerator = get_numerator_for_sig_change(changes[index_time_sig])
            denominator = changes[index_time_sig].denominator
            while index_time_sig == len(changes) - 1 or beats[current_beat_index] < changes[index_time_sig + 1].time:
                current_beat_index += numerator
                if current_beat_index > len(beats) - 1:
                    return bar_to_time_dict
                current_bar +=1
                bar_to_time_dict[current_bar] = beats[current_beat_index]
    return bar_to_time_dict

if __name__ == "__main__": 
    midi_slicer() 
