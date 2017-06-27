from flask import Flask, render_template, url_for, flash, redirect
from flask_bootstrap import Bootstrap
from forms import MusicianForm, FHIR_form
from sparql_db import SPARQL_Query, FHIR_query
from fhir_api import FHIRQueryByID

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = "Thisisasecret"


@app.route('/music/', methods=['GET', 'POST'])
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


@app.route('/fhir/')
def fhir():
    q = FHIR_query()
    results_1 = q.patient_data_query()
    results_2 = q.patient_data_query_2()
    results_3 = q.patient_data_query_3()
    return render_template('fhir.html', results_1=results_1, results_2=results_2, results_3=results_3)


@app.route('/', methods=['GET', 'POST'])
def fhir_query():
    form = FHIR_form()
    try:
        if form.validate_on_submit():
            x = FHIRQueryByID(form.resource_id.data)
            name = x.getName()
            birthdate = x.getBirthDate()
            gender = x.getGender()
            patientURL = x.getPatientURL()
            diagnoses = x.getConditionData()
            return render_template('fhir_results.html', name=name, birthdate=birthdate, gender=gender, patientURL=patientURL, diagnoses=diagnoses)
        else:
            return render_template('FHIR_query.html')
    except:
        flash('Enter valid resource ID')
        return render_template('FHIR_query.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
