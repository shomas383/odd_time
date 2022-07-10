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
    i = 0 #define variable to store current index
    #Load via pretty_midi
    pm = pretty_midi.PrettyMIDI(file)
    tempo = note_seq_sample.tempos[0].qpm
    end_time = pm.get_end_time()
    delta_time = len(pm.time_signature_changes)
    delta_array = [change.time for change in pm.time_signature_changes]
    delta_array.append(end_time)
    print(delta_array)
    # Will create slicing_midi for each time sig. change
    for slice in pm.time_signature_changes:
        print("Creating empty pretty")
        new_pm = pretty_midi.PrettyMIDI(initial_tempo=tempo) #create empty pretty object, assume fixed tempo
        ts = pretty_midi.TimeSignature(slice.numerator,slice.denominator,0)
        new_pm.time_signature_changes.append(ts)
        #loop through the original midi to retrieve all the instruments(channels) and apply it to new_pm
        current_time = slice.time
        for inst in pm.instruments:
            prog = inst.program
            is_d = inst.is_drum
            na = inst.name
            instrument = pretty_midi.Instrument(program=prog,is_drum=is_d,name=na) #create empty instruments
            new_pm.instruments.append(instrument)
        for inst,new_inst in zip(pm.instruments,new_pm.instruments):
            for notes in inst.notes: #This is the original notes that we want to copy to another object
                current_t = delta_array[i]
                next_t = delta_array[i+1]
                if notes.start >= current_t and notes.end <= next_t:
                    notes.start = notes.start - current_time
                    notes.end = notes.end - current_time
                    new_inst.notes.append(notes)

                
        print("Completed all channel")
        name = str(slice.numerator)+ "_" + str(slice.denominator) + "_" + str(slice.time) + ".mid"
        print("Writing out")
        midi_path = os.path.join(generated_path,name)
        new_pm.write(midi_path)
        print("Writing done")
        i+= 1
        print(i)

if __name__ == "__main__": 
    midi_slicer() 
