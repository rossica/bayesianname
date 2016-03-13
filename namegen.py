import random
import pickle

# Parses names into inter-letter dependencies
def parse_name(dicts_and_counts, in_name):
    name = in_name.lower()
    prev_letter = '^'
    dicts = dicts_and_counts[0]
    counts = dicts_and_counts[1]
    
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
def parse_name2(dicts_and_counts, in_name, size=1, cross_pollinate=True):
    name = in_name.lower()
    prev_symbol = '^'
    idx = 0
    dicts = dicts_and_counts[0]
    counts = dicts_and_counts[1]
    
    # Iterate over all symbols of length 'size' in 'name', including the
    # fractional last symbol, which may be less than 'size' in length
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


# Convenience function to provide previous functionality in parse_names_from_file
def parse_name2b(dicts_and_counts, in_name, size=1, cross_pollinate=True):
    symbol_size = size
    while symbol_size > 0:
        parse_name2(dicts_and_counts, in_name, symbol_size, cross_pollinate)
        symbol_size -= 1


# parses names into a probabilistic trie
# a node in this trie is a tuple of the form: (symbol, symbol_count child_count, child_dict)
## Note: Not doing this because it wont generate random new names, it'll only return names
## it was trained with.
def parse_name3(root, size, in_name): pass

# 'y' in faye is incorrectly categorized as a consonant, and not a vowel
# BUG: 'y' between two vowels is usually a consonant, but sometimes is a vowel. Can't create rules for this.
def is_consonant(idx, name):
    consonants = ('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm',
                  'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z')
    vowels = ('a', 'e', 'i', 'o', 'u')
    
    if name[idx] in consonants or (name[idx] == 'y' and ((idx < (len(name)-1) and name[idx+1] in vowels))):
        if name[idx] == 'y' and (idx > 0 and (name[idx-1] in consonants)):
            return False
        return True
    else:
        return False


def is_vowel(idx, name):
    consonants = ('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm',
                  'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z')
    vowels = ('a', 'e', 'i', 'o', 'u')
    
    if name[idx] in vowels or \
    (name[idx] == 'y' and ((idx > 0 and (name[idx-1] in consonants) or (idx < (len(name)-1) and name[idx+1] in consonants)))):
        return True
    else:
        if name[idx] == 'y' and (idx == (len(name)-1) or name[idx+1] == 'y'):
            # This covers words ending in y, or the first of double-y
            return True
        return False


# Parse names into consonant/vowel symbols
def parse_name4(dicts_and_counts, in_name):
    name = in_name.lower()
    prev_symbol = '^'
    idx = 0
    dicts = dicts_and_counts[0]
    counts = dicts_and_counts[1]
    
    while idx < len(name):
        runner = idx
        
        # Count run of consonants or vowels
        if is_consonant(idx, name):
            while runner < len(name) and is_consonant(runner, name):
                runner += 1
        elif is_vowel(idx, name):
            while runner < len(name) and is_vowel(runner, name):
                runner += 1
        else:
            print("Letter is not consonant or vowel; this is an error:", name[:idx], name[idx], name[idx+1:])
            return
        
        # Make current symbol of consecutive consonants or vowels
        curr_symbol = name[idx:runner]
        
        # Add to dictionaries
        parse_name2_worker(dicts, counts, 0, False, prev_symbol, curr_symbol)
        
        prev_symbol = curr_symbol
        idx = runner
        
    # Add the end-of-word symbol
    parse_name2_worker(dicts, counts, 0, False, prev_symbol, '$')


def parse_name5_recurse(dicts_and_counts, name, symbol_size, prev_symbol, idx):
    dicts = dicts_and_counts[0]
    counts = dicts_and_counts[1]
    curr_size = 1
    
    while curr_size <= symbol_size and curr_size <= len(name):
        if idx >= len(name):
            # Add the end-of-word symbol
            parse_name2_worker(dicts, counts, curr_size, False, prev_symbol, '$')
            break
        else:
            # Side effect: when string slicing with an end point beyond
            # the end of the string, it just returns the last part of
            # string.
            curr_symbol = name[idx:idx+curr_size]
            # Add symbol
            parse_name2_worker(dicts, counts, curr_size, False, prev_symbol, curr_symbol)
            # recurse!
            parse_name5_recurse(dicts_and_counts, name, symbol_size, curr_symbol, idx+curr_size)
        
        # Don't just keep iterating if at the end of the word
        # this prevents over-counting
        if curr_size < (len(name) - idx):
            curr_size += 1
        else:
            break


# Parse name into multi-sized symbols
# This accomplishes what parse_name2's "cross_pollinate" flag was attempting
def parse_name5(dicts_and_counts, in_name, symbol_size=1):
    name = in_name.lower()
    parse_name5_recurse(dicts_and_counts, name, symbol_size, '^', 0)


# Note: can't use databases created with parse_name2 or greater
def gen_name(dicts_and_counts, len=45, ignore_ends=False):
    import random
    prev_letter = '^'
    output = []
    count = 0
    dicts = dicts_and_counts[0]
    counts = dicts_and_counts[1]
    
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


def gen_name2(dicts_and_counts, size=45, strict_length=False):
    import random
    prev_symbol = '^'
    output = []
    count = 0
    retry = 0
    dicts = dicts_and_counts[0]
    counts = dicts_and_counts[1]
    
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


def get_valid_prefix(dict, prefix):
    while (prefix != '') and (prefix not in dict.keys()):
        prefix = prefix[1:]
    
    return prefix


def gen_name3(dicts_and_counts, size, seed=0, strict_length=False, prefix=''):
    prev_symbol = '^'
    rand = random.Random()
    output = []
    count = 0
    retry = 0
    dicts = dicts_and_counts[0]
    counts = dicts_and_counts[1]
    
    if (get_valid_prefix(dicts, prefix) != ''):
        output.append(prefix)
        count = len(prefix)
        # use the prefix as provided for output, but use the closest symbol
        # actually in the dictionary for generation.
        prev_symbol = get_valid_prefix(dicts, prefix)
    
    if (seed != 0) and (seed != ""):
        rand.seed(seed)
    
    # Generate names up to size, or until end-symbol is found
    while (count < size) or ( (not strict_length) and prev_symbol != '$'):
        curr_dict = dicts[prev_symbol]
        curr_total = float(counts[prev_symbol])
        prev_num = 0.0
        r = rand.random()
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
                    prev_symbol = '$'
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
    
    return output


def gen_name3b(dicts_and_counts, size, seed=0, count=1, strict_length=False, prefix=''):
    
    if seed == 0 or seed == "":
        sr = random.SystemRandom()
        seed = sr.getrandbits(64)
    
    seedgen = random.Random(seed)
    results = []
    itr = 0
    
    while itr < count:
        temp = gen_name3(dicts_and_counts, size, seedgen.getrandbits(64), strict_length, prefix)
        results.append(temp)
        itr += 1
    
    return (seed, results)


def save_state(dicts_and_counts, filename):
    dicts = dicts_and_counts[0]
    counts = dicts_and_counts[1]
    
    output_file = open(filename, 'wb')
    
    pickle.dump(dicts, output_file, 2)
    
    pickle.dump(counts, output_file, 2)
    
    output_file.close()


def restore_state(filename):
    input_file = open(filename, 'rb')
    
    dicts = pickle.load(input_file)
    
    counts = pickle.load(input_file)
    
    input_file.close()
    
    return (dicts, counts)


# Parse names from given file, using function fn, and passes args fn_args to fn.
# Assumes file is formatted with one name per line
def parse_names_from_file(file, fn, *fn_args):
    f = open(file, 'rU')
    
    dicts_and_counts = (dict(), dict())
    
    for line in f:
        fn(dicts_and_counts, line.strip(), *fn_args)
    
    f.close()
    
    return dicts_and_counts


# Parses names from all files in folder specified by path, using function, fn,
# and passes args, fn_args, to fn.
# Assumes files are formatted with one name per line
# TODO: currently parses out extra data from SSA baby names files. Remove this.
def parse_names_from_files(path, fn, *fn_args):
    import os
    import fileinput
    files = []
    
    dicts_and_counts = (dict(), dict())
    
    entries = os.listdir(path)
    for entry in entries:
        if os.path.isfile(os.path.join(path, entry)):
            files.append(os.path.join(path,entry))
    
    f = fileinput.input(files, False, False, -1, 'rU')
    for line in f:
        fn(dicts_and_counts, line.split(',',1)[0].strip(), *fn_args)
    
    f.close()
    
    return dicts_and_counts
    

# A function to help measure the efficacy of the parsing algorithm
# by counting the number of unreachable start states (orphans)
def count_orphans(dicts):
    orphans = dicts.viewkeys()
    for key in dicts:
        orphans -= dicts[key].viewkeys()
    
    orphans -= {'^'}
    if len(orphans):
        print(list(orphans))
    return len(orphans)


# Open the output shevles with writeback=True, otherwise this will fail
# spectacularly
def merge_dbs(list_src_dbs, out_dicts_and_counts):
    out_d = out_dicts_and_counts[0]
    out_c = out_dicts_and_counts[1]
    
    for dc in list_src_dbs:
        d = dc[0]
        c = dc[1]
        # For all symbol dictionaries in the current source dictionary
        for sym in d:
            # If the symbol dictionary already exists in the merged dictionary
            if sym in out_d:
                tmp_d = out_d[sym]
                src_d = d[sym]
                
                # Iterate and merge all counts from the symbol dictionary
                for key in src_d:
                    if key in tmp_d:
                        tmp_d[key] += src_d[key]
                    else:
                        tmp_d[key] = src_d[key]
            
            # If the symbol dictionary doesn't exist in the merged dictionary
            else:
                out_d[sym] = d[sym]
        
        # For all symbols counts in the current source dictionary
        for sym in c:
            # Add the current count to the existing count
            if sym in out_c:
                out_c[sym] += c[sym]
            # Or set the count in the merged dictionary
            else:
                out_c[sym] = c[sym]
        
        # It is assumed out_d and out_c are shelves, and we sync after every add
        out_d.sync()
        out_c.sync()

