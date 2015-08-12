import random
import cPickle

name = "matthew"
dicts = {}
counts = {}

def parse_name(dicts, counts, in_name):
    name = in_name.lower()
    prev_letter = '^'
    
    for curr_letter in name :
        if prev_letter not in dicts:
            dicts[prev_letter] = {}
        
        curr_dict = dicts[prev_letter]
        
        # Increment count of current letter that follow prev letter
        if curr_letter not in curr_dict:
            curr_dict[curr_letter] = 1
        else:
            curr_dict[curr_letter] += 1
        
        # Increment total count of symbols that follow prev letter
        if prev_letter not in counts:
            counts[prev_letter] = 1
        else:
            counts[prev_letter] += 1
        
        # Move to next letter
        prev_letter = curr_letter
    
    # Add end-of-name symbol
    if prev_letter not in dicts:
        dicts[prev_letter] = {}
    
    curr_dict = dicts[prev_letter]
    
    # Increment count of names that end with prev letter
    if '$' not in curr_dict:
        curr_dict['$'] = 1
    else:
        curr_dict['$'] += 1
    
    # Increment total count of symbols that follow prev letter
    if prev_letter not in counts:
        counts[prev_letter] = 1
    else:
        counts[prev_letter] += 1


def gen_name(dicts, counts, len=45, ignore_ends=False):
    prev_letter = '^'
    output = []
    count = 0
    
    # Generate names with max length, len
    while count < len:
        curr_dict = dicts[prev_letter]
        curr_total = float(counts[prev_letter])
        prev_num = 0.0
        r = random.random()
        retry = False
        # Iterate through all letters that follow prev_letter
        for k in curr_dict:
            ratio = curr_dict[k] / curr_total
            
            # The random selector falls in the range of this letter
            if prev_num <= r < (prev_num + ratio):
                # if selected letter is end-of-word
                if k == '$':
                    # This is not very efficient
                    if ignore_ends:
                        retry = True
                        break
                    count = len
                else:
                    output.append(k)
                    prev_letter = k
                
                break
            else:
                prev_num += ratio
        
        if retry:
            continue
        
        count += 1
    
    return "".join(output)


def save_state(dicts, counts, filename):
    output_file = open(filename, 'wb')
    
    cPickle.dump(dicts, output_file)
    
    cPickle.dump(counts, output_file)
    
    output_file.close()


def restore_state(filename, dicts, counts):
    input_file = open(filename, 'rb')
    
    dicts.update(cPickle.load(input_file))
    
    counts.update(cPickle.load(input_file))
    
    input_file.close()


