from flask import Flask, url_for, render_template, request
from namegen import gen_name2, restore_state
app = Flask(__name__)

## Currently supported databases
dbs = (
        (1, "Baby names 1880-2014: 1st Order", "babynames-all-parse_name2-order1.pkl"),
        (2, "Baby names 1880-2014: 4th Order -Mix", "babynames-all-parse_name2-order4-mix.pkl"),
        (3, "Baby names 1880-2014: 4th Order -NoMix", "babynames-all-parse_name2-order4-nomix.pkl"),
        (4, "Baby names 1880-2014: Phonetic", "babynames-all-parse_name4.pkl")
       )

MAX_SIZE = 15
MIN_SIZE = 3
MAX_COUNT = 100
loaded_dbs = {}

defaults = {'databases':dbs, 'maxsz':MAX_SIZE, 'minsz':MIN_SIZE, 
            'maxct':MAX_COUNT, 'letters':7, 'cnt':10, 'strict':1,
            'selected':1}

def validate_request(db_idx, size, strict, count):
    valid_db = False
    try:
        # validate db index
        for db in dbs:
            if db[0] == int(db_idx):
                valid_db = True
                break
        
        if not valid_db:
            return False
        
        # validate size
        if not (MIN_SIZE <= int(size) <= MAX_SIZE):
            return False
        
        # validate strictness
        if strict not in ('1', '0'):
            return False
        
        # validate count
        if not (1 <= int(count) <= MAX_COUNT):
            return False
    except:
        return False
    
    return True


@app.route('/')
def form_page():
    return render_template('form.html', **defaults)


@app.route('/generate', methods=['POST'])
def generate_names():
    results = []
    vars = {}
    vars.update(defaults)
    
    if validate_request(request.form['database'], request.form['size'],
                        request.form['strict'], request.form['count']):
        db_idx = int(request.form['database']) - 1 # map it here
        size = int(request.form['size'])
        strict = int(request.form['strict'])
        count = int(request.form['count'])
        ct = 0
        
        if db_idx not in loaded_dbs:
            loaded_dbs[db_idx] = restore_state(dbs[db_idx][2])
        
        while ct < count:
            results.append(gen_name2(loaded_dbs[db_idx],size,strict).capitalize())
            ct += 1
        
        vars['letters'] = size
        vars['cnt'] = count
        vars['strict'] = int(strict)
        vars['selected'] = db_idx + 1
        vars['results'] = results
        vars['error'] = None
    else:
        vars['error'] = "Invalid parameters passed"
    
    return render_template('form.html', **vars)



if __name__ == '__main__':
    app.run()