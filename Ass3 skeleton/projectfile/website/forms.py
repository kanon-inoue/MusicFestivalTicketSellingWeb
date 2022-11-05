# Imports to access functions and add-ons
from website.models import EventGenre, EventState, EventStatus
from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField, BooleanField, DecimalField, SelectField, IntegerField, DateTimeLocalField
from wtforms.validators import InputRequired, Length, Email, EqualTo, NumberRange, Regexp, ValidationError
from flask_wtf.file import FileRequired, FileField, FileAllowed

# Allowed image file types
ALLOWED_FILE = {'PNG', 'JPG', 'JPEG', 'jpeg', 'png', 'jpg'}

# Unlike the built-in Length validator, this will remove whitespace when counting length
# to prevent users from creating  with properties that are all or mostly whitespace
def check_field_length(form, field):
    field = field.data.strip()
    if len(field) < 5:
        #flash("Your entry was too short! Must be 5 or more characters (not including spaces)", 'warning')
        raise ValidationError('Your entry was too short! Must be 5 or more characters (not including spaces)')


# creates the login information ..
class LoginForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired('Enter user name')])
    password=PasswordField("Password", validators=[InputRequired('Enter user password')])
    submit = SubmitField("Login")

# this is the registration form ..
class RegisterForm(FlaskForm):
    user_name=StringField("User Name", validators=[InputRequired()])
    email_id = StringField("Email Address", validators=[Email("Please enter a valid email")])
    
    #linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[InputRequired(),
                  EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password")
    #use reg expression to check if phone number is start with 04 and 10 digts
    phone = StringField('Mobile Number', validators=[InputRequired(), Regexp(
        '^04[0-9]{8}$', message='Must be a 10 digit number starting with 04')])
    street_no = StringField('Street No.', validators=[InputRequired(), Regexp(
        '^[0-9/]{1,9}$', message="Up to 8 numbers and a '/' allowed only")])
    street_name = StringField('Street Name', validators=[InputRequired()])
    state = SelectField('State', choices=[('QLD'), ('NSW'), ('VIC'), (
        'ACT'), ('NT'), ('TAS'), ('SA'), ('WA')], validators=[InputRequired()])
    # chosen str instead of int here to use the length validator
    postcode = StringField('Postcode', validators=[ InputRequired(), Regexp('^[0-9]{4}$', message='Must be a 4 digit number')])
    
    # submit button
    submit = SubmitField("Register")


# Event creation, allows the user to input details and create events to appear on the main page
class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[
                        InputRequired(message='Your event must have a title'), Length(min=3, max=50, 
                            message='Title must be between 4 and 50 characters'), check_field_length])
    date = DateTimeLocalField('Date and Time', format='%Y-%m-%dT%H:%M', validators=[
        InputRequired(message='Must be in the format: dd/mm/yyyy HH:MM')])
    place = StringField('Place', validators=[
                        InputRequired(message='Your event must have a place'), Length(min=1, max=40, 
                            message='Venue Name cannot be more than 40 characters'), check_field_length])
    desc = TextAreaField('Event Description', validators=[
                         InputRequired(message='Your event must have a description'), Length(max=700, 
                            message='Event Description cannot be more than 700 characters.'), check_field_length])
    image = FileField('Event Image', validators=[
        FileRequired(message='Image cannot be empty'),
        FileAllowed(ALLOWED_FILE, message='Only supports png,jpg,JPG,PNG')])
    total_tickets = IntegerField('Total Number of Tickets', 
                                 validators=[InputRequired(message='You must select how many tickets are available for purchase.'), 
                                             NumberRange(min=1, max=99999, message='Tickets must be between 1 and 99999')])
    price = DecimalField('Cost per ticket: $', validators=[InputRequired(message='You must choose a price per ticket.'), 
            NumberRange(min=0.01, max=999.99, message='Price must be between $1.00 and $999.99')])
    
    event_genre = SelectField('Choose a genre:', choices=[
                              e.name.title() for e in EventGenre], 
                              validators=[InputRequired(message='Your event must have a music genre')])
    event_state = SelectField('Choose a state:', choices=[
                             e.name.title() for e in EventState], validators=[InputRequired(message='Your event must have a state it is located in')])
    submit = SubmitField('Create Event')

# Commenting, allows user to write comments to add and appear on the event pages
class CommentForm(FlaskForm):
    text = TextAreaField('Add your comment:', validators=[
                         InputRequired(message="Your comment can't be blank"), check_field_length])
    submit = SubmitField('Submit')

# Booking, allows user to book and obtain a ticket for specific events
class BookingForm(FlaskForm):
    tickets_required = IntegerField(
        'How many tickets would you like to book?', default='1', validators=[InputRequired()])
    submit = SubmitField('Confirm Booking')

# Edit event, allows the user to edit there created events
class EditEventForm(FlaskForm):
    title = StringField('Event Title', validators=[
                        Length(min=3, max=50, message='Title cannot be more than 40 characters')])
    date = DateTimeLocalField('Date and Time', format='%Y-%m-%dT%H:%M')
    place = StringField('Place')
    desc = TextAreaField('Event Description', validators=[
                         Length(max=700, message='Event Description cannot be more than 700 characters.')])
    image = FileField('Event Image', validators=[FileAllowed(
        ALLOWED_FILE, message='Only supports png,jpg,JPG,PNG')])
    price = DecimalField('Cost per ticket: $', validators=[NumberRange(
        min=0.01, max=999.99, message='Price must be between $0.01 and $999.99')])
    event_status = SelectField('Choose a status:', choices=[
                               e.name.title() for e in EventStatus])
    submit = SubmitField('Update Event')