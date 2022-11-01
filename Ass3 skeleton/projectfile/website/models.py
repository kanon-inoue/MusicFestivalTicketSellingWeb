from . import db
from datetime import datetime
from flask_login import UserMixin
#test
class User(db.Model, UserMixin):
    __tablename__='users' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    emailid = db.Column(db.String(100), index=True, nullable=False)
	# the storage should be at least 255 chars long
    password_hash = db.Column(db.String(255), nullable=False)

    # relation to call user.comments and comment.created_by
    comments = db.relationship('Comment', backref='user')



class Booking(db.Model): # Rename to booking
    __tablename__ = 'Tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.column(db.Integer, foreign_key=True) # use db.ForeignKey instead look at how its done in comments
    user_name = db.Column(db.String(80)) # Shouldnt need as the user_id should link it to the user table
    description = db.Column(db.String(200)) # Don't need either
    currency = db.Column(db.String(3)) # Dont need
    # ... Create the Comments db.relationship
	# relation to call destination.comments and comment.destination
    comments = db.relationship('Comment', backref='destination') #Remove tickets dont need comments
    # Need to add event id to link it to the event!
    
	
    def __repr__(self): #string print method
        return "<Name: {}>".format(self.name)

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())
    #add the foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    events_id = db.Column(db.Integer, db.ForeignKey('destinations.id'))


    def __repr__(self):
        return "<Comment: {}>".format(self.text)



class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    image = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())
    #add the foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments_id = db.Column(db.Integer, db.ForeignKey('destinations.id'))
    # add currency or price
    # Need to add date and place

# Models will need some redoing. . In theory this shouldnt take that long, I am also happy to help do models
