from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from sparql_db import SPARQL_Query

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = "Thisisasecret"


class MusicianForm(FlaskForm):
    name = StringField("Enter name of artist: ", validators=[InputRequired(message='Artist name is required')])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = MusicianForm()
    q = SPARQL_Query()
    if form.validate_on_submit():
        artist_name = str(form.name.data)
        q.add_graph(str(form.name.data))
        q.do_all_inserts()
        results = q.decision_query()
        abstract = q.artist_abstract(str(form.name.data))
        return render_template('results.html', results=results, abstract=abstract, artist_name=artist_name)
    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
