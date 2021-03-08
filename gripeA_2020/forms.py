from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file  import  FileField ,  FileAllowed ,  FileRequired
#from flask_uploads import UploadSet, DOCUMENTS
import datetime

#jsonExt = UploadSet('json',DOCUMENTS)
class toolOff(FlaskForm):
    #window = SelectField('VentaBrotes', choices=[(3,"3 meses"),(6, "6 meses"), ( 9, "9 meses"), (12, "12 meses")], 
                        #validators=[DataRequired()])
    weeks = IntegerField('Semanas (Min: 4, máx: 52)',default=4)
    date = DateField('Fecha (YYYY-MM-DD)',format='%Y-%m-%d', default=datetime.datetime.now())
    #typeA = SelectField('Tipos de aves', choices= [("b", "Ambas"), ("s", "Silvestres"), ("d", "Domesticas")], validators=[DataRequired()])
    #Archivo con coeficientes del modelo
    jsonFile = FileField( 'Archvio con parámetros personalizados')
    
    submit = SubmitField('Ok')