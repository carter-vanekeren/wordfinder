from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Optional, Regexp, ValidationError
import re
from flask_wtf.form import Form

class WordForm(FlaskForm):
    invalid = False
    avail_letters = StringField("Letters", validators=[Regexp(r'^[a-z]+$', message="Must contain letters only"),Optional()])
    
    word_length = SelectField(
        "Word Length",
        choices= [(i,i) for i in range(3,11)] + [(0, "--")],
        default=0,
        coerce=int
    )
    pattern = StringField("Pattern", validators=[
        Regexp(r'^[a-z.]+$', message="Must contain only letters and periods"),
        Optional(),
    ])
    submit = SubmitField("Go")
    def validate(self):
        if not Form.validate(self):
            print('Default validation failed')
            self.invalid = False
            return False
        else: 
            if not self.pattern.data and not self.avail_letters.data:
                self.invalid = True
                return False
            else:
                self.invalid = False
                return True

csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/')
@app.route('/index')
def index():
    form = WordForm()
    return render_template("index.html", form=form)


@app.route('/words', methods=['POST','GET'])
def letters_2_words():

    form = WordForm()
    if form.is_submitted():
        if (form.validate()):
            if form.avail_letters.data:
                letters = form.avail_letters.data
            else:
                letters = ''
            length = form.word_length.data
            pattern = '^(' + form.pattern.data + ')'
        else: 
            return render_template("index.html", form=form)

    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = set()
    if length > 0:
        temp = set()
        if not letters == '':
            for word in itertools.permutations(letters, length):
                w = "".join(word)
                if w in good_words:
                    if pattern:
                        if bool(re.match(pattern, w)):
                                temp.add(w)
                    else: 
                        temp.add(w)
            word_set = sorted(temp)
        else: 
            for w in good_words:
                if pattern:
                    if bool(re.match(pattern, w)) and len(w) == length:
                        temp.add(w)
            word_set = sorted(temp)
    else:
        temp = set()
        temp2 = set()
        if letters == '':
            for w in good_words:
                if pattern:
                    if bool(re.match(pattern, w)) and len(w) == length:
                        temp.add(w)
            word_set = sorted(temp)
        else: 
            for l in range(3,len(letters)+1):
                for word in itertools.permutations(letters, l):
                    w = "".join(word)
                    if w in good_words:
                        if pattern:
                            if bool(re.match(pattern, w)):
                                temp.add(w)
                        else: 
                            temp.add(w)
        temp2 = sorted(temp)
        word_set = sorted(temp2, key=len)

    return render_template('wordlist.html',
        wordlist=word_set,
        name="CS4131")

@app.route('/proxy')
def proxy():
    result = requests.get(request.args['url'])
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp


