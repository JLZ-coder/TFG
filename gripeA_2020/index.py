from flask import Flask, render_template, request, redirect
from forms import toolOff
from werkzeug.utils import secure_filename
import mainE as main
import json
app = Flask(__name__)
app.config['SECRET_KEY'] = '12'

@app.route('/procesado', methods=["POST"])
def process():
    weeks = request.form.get("weeks")
    date = request.form.get("date")

    jsonFile = request.form.get("jsoFile")
   
    #typeA = request.form.get("typeA")
    #main.recogidaDatos(window, typeA, date)

    return render_template("procesado.html", window = weeks, date = date, jsonData= jsonFile)

@app.route('/')
def index():
    toolOff_form = toolOff()
    if toolOff_form.validate_on_submit():
        f = toolOff_form.jsonFile.data
        print(f)
    return render_template("index.html", form = toolOff_form)

if __name__ == '__main__':
    app.run(debug=True)