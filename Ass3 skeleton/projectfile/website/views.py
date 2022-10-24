from flask import Blueprint
from flask import render_template, request, redirect, redirect,url_for, send_from_directory
from .models import Events

viewsbp = Blueprint('main', __name__)

@viewsbp.route('/', methods=['GET', 'POST'])
def index():
    events_data = Events.query.all()
    return render_template('index.html', events_data=events_data)

@viewsbp.route('/search')
def search():
    if request.args['search']:
        print(request.args['search'])
        dest = "%" + request.args['search'] + '%'
        destinations = Events.query.filter(Events.description.like(dest)).all()
        return render_template('index.html', destinations=destinations)
    else:
        return redirect(url_for('main.index'))
