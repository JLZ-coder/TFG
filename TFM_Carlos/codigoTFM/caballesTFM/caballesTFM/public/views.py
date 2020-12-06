# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from caballesTFM.extensions import login_manager
from caballesTFM.public.forms import MapForm, AlertForm
from caballesTFM.user.forms import RegisterForm
from caballesTFM.user.models import User
from caballesTFM.utils import flash_errors
from caballesTFM.map import map_generate
from caballesTFM.alerts import map_alerts

from datetime import datetime
from datetime import timedelta

blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    form = MapForm(request.form)
    alertform = AlertForm(request.form)

    return render_template('public/home.html', form=form, alertform=alertform)


@blueprint.route('/history/', methods=['GET', 'POST'])
def history():

    form = MapForm(request.form)
    if request.method == 'POST':
        map_generate(form.start_date.data, form.end_date.data, int(form.specie.data))
        return render_template('public/map.html', form=form)

    end = datetime.now()
    delta = timedelta(days = 365)
    start = end - delta
    map_generate(start, end, 0)
    return render_template('public/map.html', form=form)
 

@blueprint.route('/about/')
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form)


@blueprint.route('/alerts/', methods=['GET', 'POST'])
def alerts():
    """Home page."""
    form = AlertForm(request.form)
    if request.method == 'POST':
        map_alerts(days = form.days.data)
        return render_template('public/alert_map.html', form=form)
    map_alerts(days = 30)
    return render_template('public/alert_map.html', form=form)
