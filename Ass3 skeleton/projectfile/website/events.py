from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from flask_login.utils import login_required
from .models import Event, Comment, EventStatus, Booking, EventGenre
from .forms import EventForm, CommentForm, BookingForm, EditEventForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import current_user
from datetime import datetime

eventsbp = Blueprint('events', __name__, url_prefix='/event')

@eventsbp.route('/<id>')
def show(id):
    event = Event.query.filter_by(id=id).first()
    # create the comment form
    comments_form = CommentForm()
    booking_form = BookingForm()
    if booking_form.validate_on_submit():
        return redirect(url_for('main.index'))
    return render_template('event/event_details.html', 
                event=event, form=comments_form,
                booking_form=booking_form)

@eventsbp.route('/view_all')
def view_all_events():
    events = Event.query.filter(Event.event_status != 'UNPUBLISHED').all()
    return render_template('index.html', heading='All Events', events=events)

@eventsbp.route('/view_all/state/<state_name>')
def view_events_state(state_name):
    state_name = state_name.upper()
    state_events = Event.query.filter_by(event_state=state_name).filter(
        Event.event_status != 'UNPUBLISHED').all()
    return render_template('index.html', heading=state_name, events=state_events)

@eventsbp.route('/view_all/<genre>')
def view_events_genre(genre):
    genre = genre.upper()
    event_genre_list = Event.query.filter_by(event_genre=genre).filter(
        Event.event_status != 'UNPUBLISHED').all()
    return render_template('index.html', heading=genre, events=event_genre_list)

@eventsbp.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
    form = EventForm()
    proceed = True
    
    if form.date.data != None and form.date.data < datetime.now():
        flash("You can't create an event in the past!", 'danger')
        proceed = False
        
    if form.validate_on_submit() and proceed == True:
        #call the function that checks and returns image    
        db_file_path = check_upload_file(form)
        event = Event(title=form.title.data, 
                date=form.date.data,
                place=form.place.data, 
                description=form.desc.data,
                image=db_file_path, 
                total_tickets=form.total_tickets.data, 
                tickets_remaining=form.total_tickets.data, 
                price=form.price.data, 
                event_status=EventStatus(1).name,
                event_genre=form.event_genre.data.upper(), 
                event_state=form.event_state.data.upper(), 
                user_id=current_user.id)    
        
        # add the object to the db session
        db.session.add(event)
        # commit to the database
        db.session.commit()
        print('Created new event')
        flash('Successfully created new music event', 'success')
        return redirect(url_for('main.my_events'))
    return render_template('event/create_event.html', event_form=form, heading = 'Create a New Event')

@eventsbp.route('/<id>/update', methods=['GET', 'POST'])
@login_required
def update_event(id):
    event = Event.query.get(id)
    # Provide the old event information in the form fields
    # as a reminder to the user
    form = EditEventForm(
        title=event.title,
        date=event.date,
        place=event.place,
        desc=event.description,
        total_tickets=event.total_tickets,
        price=event.price,
        event_status=event.event_status,
        event_genre=event.event_genre.name.title(),
        event_state=event.event_state.name.title())
    # First check the current user is editing
    # an event they created and not someone else's
    if current_user.id != event.user_id:
        print("You can only edit your own events!", 'danger')
        # return redirect(url_for('main.my_events'))
    if form.validate_on_submit():
        # If a new image was supplied, update it (need to check since it is not mandatory
        # to supply an image on the EditEventForm, therefore check_upload_file would write an
        # empty string to the event's image database column)
        if (form.image.data is not None):
            # call the function that checks and returns image
            db_file_path = check_upload_file(form)
            Event.query.filter_by(id=id).update(
                {'image': db_file_path}, synchronize_session='evaluate')
            Event.query.filter_by(id=id).update(
            {'title': form.title.data, 
            'date': form.date.data, 
            'place': form.place.data, 
            'description': form.desc.data,
            'price': form.price.data,
            'event_status': form.event_status.data.upper(),}, 
            synchronize_session='evaluate')
        # commit to the database
        db.session.commit()
        print('Successfully updated event!', 'success')
        # end with redirect when form is valid
        #return redirect(url_for('main.my_events'))
    return render_template('event/create_event.html', event_form=form, event=event, heading='Edit Event')

@eventsbp.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    event = Event.query.get(id)
    # Make sure the current user is deleting their own
    # event and not someone else's
    if current_user.id != event.user_id:
        print("You can only edit your own events!", 'danger')
        #return redirect(url_for('main.my_events'))
    # Delete the event from the database
    Event.query.filter_by(id=id).delete()
    # Delete any associated bookings
    # (should also delete the comments to save disk space)
    Booking.query.filter_by(event_id=id).delete()
    db.session.commit()
    #return redirect(url_for('main.my_events'))

@eventsbp.route('/<id>/comment', methods=['GET', 'POST'])
@login_required
def comment(id):
    form = CommentForm()
    # get the Event object associated to the page
    event = Event.query.filter_by(id=id).first()
    if form.validate_on_submit():
        # Create the Comment object using the form data
        comment = Comment(text=form.text.data,
                          event=event, created_at=datetime.now(), user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        # flashing a message which needs to be handled by the html
        flash('Your comment has been added', 'primary')
    # using redirect sends a GET request to destination.show
    return redirect(url_for('events.show', id=id))

@eventsbp.route('/<id>/book', methods=['GET', 'POST'])
@login_required
def book_event(id):
    form = BookingForm()
    event = Event.query.filter_by(id=id).first()
    # check to see if the booking should be allowed to go ahead
    if check_tickets(form, event):
        if form.validate_on_submit():
            # Create the new booking object
            new_booking = Booking(
                tickets_booked=form.tickets_required.data, booked_on=datetime.now(), user_id=current_user.id, event_id=id)
            # Find the event this booking is for and update its remaining tickets
            Event.query.filter_by(id=id).update(
                {'tickets_remaining': event.tickets_remaining-form.tickets_required.data, 'tickets_booked': event.tickets_booked+form.tickets_required.data}, synchronize_session='evaluate')
            db.session.add(new_booking)
            db.session.commit()
            flash_string = "Your booking was successfully created! You've been charged ${:,.2f}. Your booking reference is: {}".format(
                (event.price)*(new_booking.tickets_booked), new_booking.id)
            print(flash_string,'success')
            return redirect(url_for('events.show', id=id))
    return redirect(url_for('events.show', id=id))

def check_upload_file(form):
    # get file data from form
    fp = form.image.data
    filename = fp.filename
    # get the current path of the module file… store image file relative to this path
    BASE_PATH = os.path.dirname(__file__)
    # upload file location – directory of this file/static/image
    upload_path = os.path.join(
        BASE_PATH, current_app.config['UPLOAD_FOLDER'], secure_filename(filename))
    # store relative path in DB as image location in HTML is relative
    db_upload_path = '/' + \
        current_app.config['UPLOAD_FOLDER'] + secure_filename(filename)
    # save the file and return the db upload path
    fp.save(upload_path)
    return db_upload_path

# Function to check if a booking should be allowed to execute
def check_tickets(form, event):
    # Form data will be None if input is not an integer 
    # since the FormField is IntegerField
    if form.tickets_required.data is None:
        print("You must enter only a whole number!", 'warning')
        return False
    # If some idiot is trying to book no tickets or negative tickets
    elif form.tickets_required.data <= 0:
        print("You must book at least one ticket!", 'warning')
        return False
    # Otherwise, if their booking will result in negative tickets
    elif event.tickets_remaining - form.tickets_required.data < 0:
        print("Your order cannot be placed as it exceeds the number of tickets remaining. Reduce the quantity and try again.", 'danger')
        return False
    # Otherwise let the booking go ahead
    else:
        # If this booking exhausts the remaining tickets, set it to Booked Out
        if event.tickets_remaining - form.tickets_required.data == 0:
            event.event_status = EventStatus.BOOKED
            return True
    return True 