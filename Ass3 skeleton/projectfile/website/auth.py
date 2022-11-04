from flask import Blueprint, render_template, request,redirect,url_for,flash
from .forms import LoginForm, RegisterForm
#new imports:
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash,check_password_hash
from .models import User
from . import db

#create a blueprint
authbp = Blueprint('auth', __name__ )

# Checks if the current user is Anonymous or logged in
def is_current_user():
    if current_user.name == 'Guest':
        name = 'Guest'
    else:
        name = current_user.name
    return name

@authbp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    register = RegisterForm()
    address = []
    #the validation of form submis is fine
    if (register.validate_on_submit() == True):
            #get username, password and email from the form
            uname =register.user_name.data
            pwd = register.password.data
            email=register.email_id.data
            #get phone num from the form
            phonenum = register.phone.data
            #get address from the form
            streetnum = register.street_no.data
            streetname = register.street_name.data
            statename = register.state.data
            pcode = register.postcode.data
            address.append(str(streetnum))
            address.append(streetname)
            address.append(statename)
            address.append(str(pcode))
            address_string = ' '.join(str(item) for item in address)
            
            #check if a user exists
            u1 = User.query.filter_by(name=uname).first()
            u1 = User.query.filter_by(emailid=email).first()
            if u1:
                flash('User name already exists, please login')
                return redirect(url_for('auth.login'))
            
            # don't store the password - create password hash
            pwd_hash = generate_password_hash(pwd)
            
            #create a new user model object
            new_user = User(name=uname, password_hash=pwd_hash, emailid=email, 
                            phone=phonenum, address= address_string)
            db.session.add(new_user)
            db.session.commit()
            #commit to the database and redirect to HTML page
            return redirect(url_for('auth.login'))
    #the else is called when there is a get message
    else:
        return render_template('user.html', form=register, heading='Register')

@authbp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    error=None
    if(login_form.validate_on_submit()==True):
        #get the username and password from the database
        user_name = login_form.user_name.data
        password = login_form.password.data
        
        remember = True if request.form.get('remember') else False
        
        u1 = User.query.filter_by(name=user_name).first()
        #if there is no user with that name
        if u1 is None:
            error='Incorrect user name'

        #check the password - notice password hash function
        elif not check_password_hash(u1.password_hash, password): # takes the hash and password
            error='Incorrect password'
    
        if error is None:
            #all good, set the login_user of flask_login to manage the user
            login_user(u1, remember=remember)
            print('Successfully logged in')
            flash('You logged in successfully', 'success')
            return redirect(url_for('main.index'))
        
        else:
            flash(error)
            return redirect(url_for('auth.login'))
            
    return render_template('user.html', form=login_form, heading='Login')

@authbp.route('/logout')
@login_required
def logout():
    #logout user
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))