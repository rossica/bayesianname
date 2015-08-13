import random
import cPickle

name = "matthew"
dicts = {}
counts = {}

# Parses names into inter-letter dependencies
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


def parse_name2_worker(dicts, counts, size, cross_pollinate, prev_symbol, curr_symbol):
    if prev_symbol not in dicts:
            dicts[prev_symbol] = {}
    
    curr_dict = dicts[prev_symbol]
    
    # add current symbol to current dictionary
    if curr_symbol not in curr_dict:
        curr_dict[curr_symbol] = 1
    else:
        curr_dict[curr_symbol] += 1
    
    # Increment total symbols for prev_symbol
    if prev_symbol not in counts:
        counts[prev_symbol] = 1
    else:
        counts[prev_symbol] += 1
    
    # TODO: cross_pollinate doesn't work well; it creates orphans
    # also add to dictionary of sub-symbols of prev_symbol
    if cross_pollinate:
        # don't double-add the first symbol or single-letter symbols
        if prev_symbol != '^' and len(prev_symbol) > 1:
            prev_symbol_end = prev_symbol[-(size-1):]
            if prev_symbol_end not in dicts:
                dicts[prev_symbol_end] = {}
            
            other_dict = dicts[prev_symbol_end]
            
            if curr_symbol not in other_dict:
                other_dict[curr_symbol] = 1
            else:
                other_dict[curr_symbol] += 1
            
            if prev_symbol_end not in counts:
                counts[prev_symbol_end] = 1
            else:
                counts[prev_symbol_end] += 1



# parses names into symbols which may be longer than 1 letter and stores
# inter-symbol dependencies
def parse_name2(dicts, counts, size, in_name, cross_pollinate=True):
    name = in_name.lower()
    prev_symbol = '^'
    idx = 0
    
    # Iterate over all symbols of length 'size' in 'name', including the fractional
    # last symbol, which may be less than 'size' in length
    while idx < len(name):
        # Side effect: when string slicing with an end point beyond
        # the end of the string, it just returns the last part of
        # string.
        curr_symbol = name[idx:idx+size]
        
        parse_name2_worker(dicts, counts, size, cross_pollinate, prev_symbol, curr_symbol)
        
        # Move to the next symbol
        prev_symbol = curr_symbol
        idx += size
    
    # Add the end-of-word symbol
    parse_name2_worker(dicts, counts, size, cross_pollinate, prev_symbol, '$')


# parses names using a sliding window
def parse_name3(): pass

# Note: can't use databases created with parse_name2
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


def gen_name2(dicts, counts, size=45, strict_length=False):
    prev_symbol = '^'
    output = []
    count = 0
    retry = 0
    
    # Generate names with max length, size
    while count < size:
        curr_dict = dicts[prev_symbol]
        curr_total = float(counts[prev_symbol])
        prev_num = 0.0
        r = random.random()
        # Iterate through all letters that follow prev_symbol
        for k in curr_dict:
            ratio = curr_dict[k] / curr_total
            
            # The random selector falls in the range of this symbol
            if prev_num <= r < (prev_num + ratio):
                if strict_length:
                    # This is not very efficient
                    if k == '$' or (len(k) + count) > size:
                        retry += 1
                        break
                
                # if selected symbol is end-of-word
                if k == '$':
                    count = size
                else:
                    retry = 0
                    output.append(k)
                    prev_symbol = k
                
                break
            else:
                prev_num += ratio
        
        # Prevent infinite loops in conditions that cannot be met
        if retry > 10000:
            break
        elif retry > 0:
            continue
        
        retry = 0
        count += len(prev_symbol)
    
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


def parse_names_from_file(size, file, dicts, counts):
    f = open(file, 'rU')
    
    for line in f:
        symbol_size = size
        while symbol_size > 0:
            parse_name2(dicts, counts, symbol_size, line.strip())
            symbol_size -= 1
    
    f.close()


# A function to help measure the efficacy of the parsing algorithm
# by counting the number of unreachable start states (orphans)
def count_orphans(dicts):
    orphans = {}
    for k in dicts:
        is_orphan = True
        for k2 in dicts:
            for k3 in dicts[k2]:
                if k3 == k:
                    is_orphan = False
                    break
         
        # don't count start symbol as orphan
        if is_orphan and k != '^':
            orphans[k] = ''
    
    if len(orphans):
        print list(orphans.viewkeys())
    return len(orphans)


