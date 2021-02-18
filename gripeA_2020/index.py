from flask import Flask, render_template, request, redirect
from forms import toolOff
import mainE as main
app = Flask(__name__)
app.config['SECRET_KEY'] = '12'

@app.route('/procesado', methods=["POST"])
def process():
    window = request.form.get("window")
    date = request.form.get("date")
    typeA = request.form.get("typeA")
    #main.recogidaDatos(window, typeA, date)

    return render_template("procesado.html", window = window, date = date, typeA= typeA)

@app.route('/')
def index():
    toolOff_form = toolOff()
    return render_template("index.html", form = toolOff_form)

if __name__ == '__main__':
    app.run(debug=True)