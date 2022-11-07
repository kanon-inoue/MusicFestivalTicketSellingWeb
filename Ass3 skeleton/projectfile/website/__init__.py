#import flask - from the package import class
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import datetime
from werkzeug.exceptions import HTTPException
import os

db = SQLAlchemy()
#app = Flask(__name__) # this is the name of the module/package that is calling this app

#create a function that creates a web application
# a web server will run this web application
def create_app():
    # this is the name of the module/package that is calling this app
    app = Flask(__name__)
    #we use this utility module to display forms quickly
    bootstrap = Bootstrap(app)
    # a secret key for the session object
    app.secret_key = 'abcde'
    # configue and initialise DB
    app.config['SQLALCHEMY_DATABASE_URI']=os.environ['sqlite:///music_events.sqlite']
    app.config['UPLOAD_FOLDER'] = 'static/images/'
    #initialize db with flask app
    db.init_app(app)
    
    #initialize the login manager
    login_manager = LoginManager()
    from .models import User, Anonymous  # importing here to avoid circular references
    login_manager.anonymous_user = Anonymous
    login_manager.login_message_category = "warning"
    #set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view='auth.login'
    login_manager.init_app(app)
     
    # add blueprints
    # importing views module here to avoid circular references a commonly used practice.
    from . import views, events, auth
    app.register_blueprint(views.viewsbp)
    app.register_blueprint(events.eventsbp)
    app.register_blueprint(auth.authbp)
    
    #create a user loader function takes userid and returns User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def get_context():
        # Checks if the current user is Anonymous or logged in
        if current_user.name == 'Guest':
            name = 'Guest'
        else:
            name = current_user.name
        from website.models import Event, EventState, EventGenre, EventStatus
        all_events = Event.query.all()
        # On launch, check if there are any events that are now in the past
        # and if so, change them to Inactive
        for event in all_events:
            if event.date < datetime.now():
                event.event_status=EventStatus.INACTIVE
        current_events = Event.query.filter(Event.event_status!='INACTIVE')
        db.session.commit()
        dropdown_events = Event.query.group_by(Event.title).filter(
        Event.event_status != 'INACTIVE').all()
        genres = EventGenre
        states = EventState
        return(dict(events_list=all_events, artist_list=dropdown_events,
                    genres=genres, states=states,
                    username=name, current_events=current_events))

    @app.errorhandler(404)
    # inbuilt function which takes error as parameter
    def not_found(e):  # error view function
        return render_template('404.html'), 404


    return app