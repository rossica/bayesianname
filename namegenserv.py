from flask import Flask, url_for, render_template, request
from namegen import gen_name2, gen_name3b, restore_state
import shelve
import re
app = Flask(__name__)

## Currently supported databases
dbs = (
        (1, "1-Letter chunks", "babynames-all-parse_name2-order1.pkl", "Baby Names 1880-2014", False),
        (2, "4,3,2,1-letter chunks mixed", "babynames-all-parse_name5-order4-mix.pkl", None, False),
        (3, "4-letter chunks", "babynames-all-parse_name2-order4-nomix.pkl", None, False),
        (4, "Phonetic (consonant/vowel)", "babynames-all-parse_name4.pkl", None, True),
        (5, "1-letter chunks", "surnames-parse_name2-order1.pkl", "Surnames 2000 US Census", False),
        (6, "Phonetic (consonant/vowel)", "surnames-parse_name4.pkl", None, True),
        (7, "All databases merged", ("everything2-sym.shlv", "everything2-cnt.shlv"), None, False)
       )

MAX_SIZE = 15
MIN_SIZE = 3
MAX_COUNT = 100
loaded_dbs = {}

default_parms = {'databases':dbs, 'maxsz':MAX_SIZE, 'minsz':MIN_SIZE,
            'maxct':MAX_COUNT, 'letters':7, 'cnt':10, 'strict':1,
            'selected':4, 'show':0}

def validate_request(form):
    clean_form = {}
    valid_db = False
    try:
        # validate db index
        for db in dbs:
            if db[0] == int(form['database']):
                valid_db = True
                break
        
        if not valid_db:
            return ("Invalid database", clean_form)
        else:
            clean_form['database'] = int(form['database'])
        
        # validate size
        if not (MIN_SIZE <= int(form['size']) <= MAX_SIZE):
            return ("Invalid letter count", clean_form)
        else:
            clean_form['size'] = int(form['size'])
        
        # validate strictness
        if form['strict'] not in ('1', '0'):
            return ("Invalid boolean value", clean_form)
        else:
            clean_form['strict'] = int(form['strict'])
        
        # validate count
        if not (1 <= int(form['count']) <= MAX_COUNT):
            return ("Invalid number of names", clean_form)
        else:
            clean_form['count'] = int(form['count'])
         
         # validate show symbols
        if form['show'] not in ('1', '0'):
            return ("Invalid boolean value", clean_form)
        else:
            clean_form['show'] = int(form['show'])
        
        # validate user_seed
        if not form.has_key('user_seed'):
            clean_form['user_seed'] = 0
        else:
            try:
                clean_form['user_seed'] = int(form['user_seed'])
            except:
                clean_form['user_seed'] = form['user_seed']
        
        # validate user prefix
        if not form.has_key('prefix'):
            clean_form['prefix'] = ''
        else:
            clean_form['prefix'] = re.sub('[^a-zA-Z]','',form['prefix'])
        
    except:
        return ("Type conversion error", clean_form)
    
    return (None, clean_form)


@app.route('/')
def form_page():
    return render_template('form.html', **default_parms)


@app.route('/generate/', methods=['POST'])
def generate_names():
    results = []
    vars = {}
    vars.update(default_parms)
    
    error, clean_form = validate_request(request.form)
    
    if (error == None):
        db_idx = clean_form['database'] - 1 # map it here
        size = clean_form['size']
        strict = clean_form['strict']
        count = clean_form['count']
        show = clean_form['show']
        user_seed = clean_form['user_seed']
        prefix = clean_form['prefix']
      
        if db_idx not in loaded_dbs:
            # Ugly hack to special-case the everything database in a shelf
            if db_idx == 6:
                loaded_dbs[db_idx] = (shelve.open(dbs[db_idx][2][0],
                                                  flag='r',
                                                  protocol=2),
                                      shelve.open(dbs[db_idx][2][1],
                                                  flag='r',
                                                  protocol=2))
            else:
                loaded_dbs[db_idx] = restore_state(dbs[db_idx][2])
        
        results = gen_name3b(loaded_dbs[db_idx], size, user_seed, count, strict, prefix)
        
        if(user_seed != 0 and user_seed != ""):
            vars['user_seed'] = user_seed
        if(prefix != ""):
            vars['prefix'] = prefix
        vars['letters'] = size
        vars['seed'] = results[0]
        vars['cnt'] = count
        vars['strict'] = strict
        vars['selected'] = db_idx + 1
        vars['results'] = results[1]
        vars['show'] = show
        vars['error'] = None
    else:
        vars.update(clean_form)
        vars['error'] = "Invalid parameter error: "
        vars['reason'] = error
    
    return render_template('form.html', **vars)



if __name__ == '__main__':
    app.run()