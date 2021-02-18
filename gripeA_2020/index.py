from flask import Flask, render_template, request, redirect
from forms import toolOff
import mainE as main
app = Flask(__name__)
app.config['SECRET_KEY'] = '12'

@app.route('/', methods=["GET", "POST"])
def index():
    toolOff_form = toolOff()
    if toolOff_form.validate_on_submit():
        window = toolOff_form.window.data
        date = toolOff_form.date.data
        typeA = toolOff_form.typeA.data
        main.recogidaDatos(window, typeA, date)



    return render_template("index.html", form = toolOff_form)

if __name__ == '__main__':
    app.run(debug=True)