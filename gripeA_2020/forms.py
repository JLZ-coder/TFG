from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField,SelectField
from wtforms.validators import DataRequired, Email, Length
import datetime


class toolOff(FlaskForm):
    window = SelectField('VentaBrotes', choices=[(3,"3 meses"),(6, "6 meses"), ( 9, "9 meses"), (12, "12 meses")], 
                        validators=[DataRequired()])
    date = DateField('Fecha',format="%Y-%m-%d", 
                        default=datetime.datetime.now(),
                        validators=[DataRequired()])
    typeA = SelectField('Tipos de aves', choices= [("b", "Ambas"), ("s", "Silvestres"), ("d", "Domesticas")], validators=[DataRequired()])
    #Coeficientes del modelo
    
    submit = SubmitField('Ok')