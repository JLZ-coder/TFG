from flask import Flask, render_template, request, redirect
from forms import toolOff

app = Flask(__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'

@app.route('/', methods=["GET", "POST"])
def index():
    toolOff_form = toolOff()
    if toolOff_form.validate_on_submit():
        window = form.window.data
        date = form.date.data
        typeA = form.password.data
        
    return render_template("index.html", form = toolOff_form)

if __name__ == '__main__':
    app.run(debug=True)