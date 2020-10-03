# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, DateTimeField, SelectField
from wtforms.validators import DataRequired
from datetime import datetime
from caballesTFM.user.models import User


class MapForm(FlaskForm):


    start_date =  StringField('Fecha Inicio', validators=[DataRequired()], default=datetime.now().date())
    end_date = StringField('Fecha Fin', validators=[DataRequired()], default=datetime.now().date())
    specie =  SelectField('Especie', choices=[('1340', 'Ciconia ciconia'), ('1610', 'Anser anser'), ('0', 'Todos')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(MapForm, self).__init__(*args, **kwargs)
        self.user = None


class AlertForm(FlaskForm):

    days =  SelectField('Días previos', choices=[(90, '3 Meses'), (180, '6 Meses'), (365, '1 Año')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(AlertForm, self).__init__(*args, **kwargs)
        self.user = None


