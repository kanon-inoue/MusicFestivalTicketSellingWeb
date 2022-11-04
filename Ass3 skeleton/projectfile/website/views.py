from flask import Blueprint
from flask import render_template, request, redirect, redirect,url_for, send_from_directory
from flask_login.utils import login_required, current_user
from .models import Event

# Allows for routing and assigning tags to python code
viewsbp = Blueprint('main', __name__)

def is_current_user():
    if is_current_user.name == 'Guest':
        name = 'Guest'
    else:
        name = current_user.name
    return name

# Displays the main home page or index page
@viewsbp.route('/', methods=['GET', 'POST'])
def index():
    events_data = Event.query.all()
    return render_template('index.html', events_data=events_data)

# Allows user to search for specific events and filter the events based on the recieved search phrase filter
@viewsbp.route('/search')
def search():
    if request.args['search']:
        print(request.args['search'])
        event = "%" + request.args['search'] + '%'
        events_data = Event.query.filter(Event.description.like(event)).all()
        return render_template('index.html', events_data=events_data)
    else:
        return redirect(url_for('main.index'))

@viewsbp.route('/my_event')
@login_required
def my_events():
    return render_template('event/myevents.html', heading='My Events', events=current_user.created_events)
