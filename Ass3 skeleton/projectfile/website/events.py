from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login.utils import login_required
from .models import Event, Comment, EventCity, EventGenre, EventStatus, Booking # add state and date
from .forms import EditEventForm, EventForm, CommentForm, BookingForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import current_user

eventbp = Blueprint('events', __name__, url_prefix='/events')


@eventbp.route('/<id>')
def show(id):
    event = Event.query.filter_by(id=id).first()
    # create the comment form
    comments_form = CommentForm()
    booking_form = BookingForm()
    if booking_form.validate_on_submit():
        return redirect(url_for('main.index'))
    artist_events = Event.query.filter_by(headliner=event.headliner).all()
    return render_template('events/eventDetails.html', event=event, form=comments_form, booking_form=booking_form, artist_events=artist_events)


@eventbp.route('/view_all')
def view_all_events():
    events = Event.query.filter(Event.event_status != 'INACTIVE').all()
    return render_template('events/view_events.html', heading='All Events', events=events)


@eventbp.route('/view_all/city/<state_name>')
def view_events_state(state_name):
    state_name = state_name.upper()
    event_state_list = Event.query.filter_by(event_state=state_name).filter(
        Event.event_status != 'INACTIVE').all()
    return render_template('events/view_events.html', heading=state_name, events=event_state_list)


@eventbp.route('/view_all/<genre>')
def view_events(genre):
    genre = genre.upper()
    genre_events_list = Event.query.filter_by(event_genre=genre).filter(
        Event.event_status != 'INACTIVE').all()
    return render_template('events/view_events.html', heading=genre, events=genre_events_list)


@eventbp.route('/view_all/<date>')
def view_events(date):
    date = date.upper()
    event_dates_list = Event.query.filter_by(event_date=date).filter(
        Event.event_status != 'INACTIVE').all()
    return render_template('events/view_events.html', heading=date, events=event_dates_list)


@eventbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()
    proceed = True
    if form.date.data != None and form.date.data < datetime.now():
        flash("You can't create an event in the past!", 'danger')
        proceed = False
        #return redirect(url_for('main.my_events'))
    if form.validate_on_submit() and proceed == True:
        # call the function that checks and returns image
        db_file_path = check_upload_file(form)
        event = Event(title=form.title.data, date=form.date.data, headliner=form.headliner.data, venue=form.venue.data, description=form.desc.data,
                      image=db_file_path, total_tickets=form.total_tickets.data, tickets_remaining=form.total_tickets.data, price=form.price.data, event_status=EventStatus(
                          1).name,
                      event_genre=form.event_genre.data.upper(), event_city=form.event_city.data.upper(), created_on=datetime.now(), user_id=current_user.id)
        # add the object to the db session
        db.session.add(event)
        # commit to the database
        db.session.commit()
        flash('Successfully created new event','success')
        print('Successfully created new event')
        # Always end with redirect when form is valid
        return redirect(url_for('main.my_events'))
    return render_template('events/create_event.html', event_form=form, heading='Create a new Event')


@eventbp.route('/<id>/update', methods=['GET', 'POST'])
@login_required
def update_event(id):
    event = Event.query.get(id)
    # Provide the old event information in the form fields
    # as a reminder to the user
    form = EditEventForm(
        title=event.title,
        date=event.date,
        headliner=event.headliner,
        venue=event.venue,
        desc=event.description,
        total_tickets=event.total_tickets,
        price=event.price,
        event_status=event.event_status,
        event_genre=event.event_genre.name.title(),
        event_city=event.event_city.name.title())
    # First check the current user is editing
    # an event they created and not someone else's
    if current_user.id != event.user_id:
        flash("You can only edit your own events!", 'danger')
        return redirect(url_for('main.my_events'))
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
            {'title': form.title.data, 'date': form.date.data, 'headliner': form.headliner.data,
             'venue': form.venue.data, 'description': form.desc.data,
             'total_tickets': form.total_tickets.data,
             'tickets_remaining': form.total_tickets.data-event.tickets_booked,
             'price': form.price.data,
             'event_status': form.event_status.data.upper(), 'event_genre': form.event_genre.data.upper(),
             'event_city': form.event_city.data.upper()}, synchronize_session='evaluate')
        # commit to the database
        db.session.commit()
        flash('Successfully updated event!', 'success')
        # end with redirect when form is valid
        return redirect(url_for('main.my_events'))
    return render_template('events/create_event.html', event_form=form, event=event, heading='Edit Event')


@eventbp.route('/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    event = Event.query.get(id)
    # Make sure the current user is deleting their own
    # event and not someone else's
    if current_user.id != event.user_id:
        flash("You can only edit your own events!", 'danger')
        return redirect(url_for('main.my_events'))
    # Delete the event from the database
    Event.query.filter_by(id=id).delete()
    # Delete any associated bookings
    # (should also delete the comments to save disk space)
    Booking.query.filter_by(event_id=id).delete()
    db.session.commit()
    return redirect(url_for('main.my_events'))


@eventbp.route('/<id>/comment', methods=['GET', 'POST'])
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


@eventbp.route('/<id>/book', methods=['GET', 'POST'])
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
            flash(flash_string,'success')
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
        flash("You must enter only a whole number!", 'warning')
        return False
    # If some idiot is trying to book no tickets or negative tickets
    elif form.tickets_required.data <= 0:
        flash("You must book at least one ticket!", 'warning')
        return False
    # Otherwise, if their booking will result in negative tickets
    elif event.tickets_remaining - form.tickets_required.data < 0:
        flash("Your order cannot be placed as it exceeds the number of tickets remaining. Reduce the quantity and try again.", 'danger')
        return False
    # Otherwise let the booking go ahead
    else:
        # If this booking exhausts the remaining tickets, set it to Booked Out
        if event.tickets_remaining - form.tickets_required.data == 0:
            event.event_status = EventStatus.BOOKED
            return True
    return True