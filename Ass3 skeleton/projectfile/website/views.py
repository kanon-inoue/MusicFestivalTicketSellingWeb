from flask import Blueprint
from flask import render_template, request, redirect, redirect,url_for, send_from_directory
from .models import Events

# Allows for routing and assigning tags to python code
viewsbp = Blueprint('main', __name__)

# Displays the main home page or index page
@viewsbp.route('/', methods=['GET', 'POST'])
def index():
    events_data = Events.query.all()
    return render_template('index.html', events_data=events_data)

# Allows user to search for specific events and filter the events based on the recieved search phrase filter
@viewsbp.route('/search')
def search():
    if request.args['search']:
        print(request.args['search'])
        event = "%" + request.args['search'] + '%'
        events_data = Events.query.filter(Events.description.like(event)).all()
        return render_template('index.html', events_data=events_data)
    else:
        return redirect(url_for('main.index'))