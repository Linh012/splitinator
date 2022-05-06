from flask import Flask, render_template, redirect, flash, url_for, request
from flask_sqlalchemy import SQLAlchemy
from config import *
from forms import LoginForm, RegisterForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig') # import configuration
db = SQLAlchemy(app)

from models import User, Bill, House, dbinit, Message # avoid circular import
db.create_all() # create database tables

# user session manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need to be logged in!"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# reset dummy data
@app.route('/resetdb')
def resetdb():
    db.drop_all()
    db.create_all()
    dbinit()
    return redirect('/')


# index page
@app.route('/')
def index():
    return render_template('index.html')


# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard')) # redirect to dashboard if already logged in

    forms = LoginForm()

    if forms.validate_on_submit():
        user = User.query.filter_by(email=forms.email.data).first() # query database for user

        if user is None:
            flash("no user found")
            return redirect(url_for('login'))
        if not check_password_hash(user.hashed_password, forms.password.data): # check correct password
            flash("wrong password")
            return redirect(url_for('login'))

        login_user(user, remember=forms.remember_me.data) # new user session
        return redirect(url_for('dashboard'))

    return render_template("login.html", forms=forms)


# sign up page
@app.route('/register', methods=['GET', 'POST'])
def register():
    forms = RegisterForm()

    if forms.validate_on_submit():
        username = forms.username.data
        email = forms.email.data
        
        password = forms.password.data
        passwordconfirm = forms.passwordconfirm.data
        if (password != passwordconfirm): # check both password match
            flash("Password missmatch")
            return redirect(url_for('register'))
        
        user_used = User.query.filter_by(username=username).first()
        if user_used: # check if username already in use
            flash("username already in use!")
            return redirect(url_for('register'))
        
    
        email_used = User.query.filter_by(email=email).first()
        if email_used: # check if email already in use
            flash("email already in use!")
            return redirect(url_for('register'))      

    
        user = User(username=username, email=email, hashed_password=generate_password_hash(password), home=None)
        db.session.add(user) # add new user to database
        db.session.commit()
        flash("Successful registration")
        return redirect(url_for('login'))

    return render_template("register.html", forms=forms)


# logout
@app.route('/logout')
@login_required
def logout():
    logout_user() # delete user session/cookie
    flash("Successful logout")
    return redirect(url_for('index'))


# dashboard page
@app.route('/dashboard')
@login_required
def dashboard():
    userid = current_user.id
    user = User.query.filter_by(id=userid).first()

    messages = Message.query.filter_by(user_id=userid).all()
    if messages: # get any messages sent by other housemates
        for m in messages:
            flash(m.message)
            db.session.delete(m)
        
        db.session.commit()


    bills = Bill.query.filter_by(user_id=userid).all()
    house = House.query.filter_by(id=user.home).first()
    if house: # if user has housemates
        housemates = User.query.filter_by(home=house.id).all()
        owed = []
        for mate in housemates: # get each housemate's bills
            mate_bills = Bill.query.filter_by(user_id=mate.id).all()
            owed.append(mate_bills)        

        matesAnddebt = list(zip(housemates, owed)) # join housemates and their bills
    else:
        matesAnddebt = None

    return render_template('dashboard.html', user=user, bills=bills, housemates=matesAnddebt)


# create and add new bill to database
@app.route('/addBill', methods=['POST'])
@login_required
def addBill():
    userid = current_user.id
    deets = request.form['billDetails']
    amount = request.form['billAmount']
    bill = Bill(amount, deets, userid)
    db.session.add(bill)
    db.session.commit()
    flash("New bill added successfully")
    return redirect(url_for('dashboard'))


# pay bill and commit changes to database
@app.route('/payBill', methods=['POST'])
@login_required
def payBill():
    bill_id = request.form['billId']
    pay_amount = float(request.form['payAmount'])
    bill = Bill.query.filter_by(id=bill_id).first()
    if (pay_amount >= bill.amount): # delete bill if bill fully paid off
        db.session.delete(bill)
        flash("Bill payment complete! It has been removed from the table.")
    else:
        bill.amount = (bill.amount - pay_amount)
        flash("Success payment operation.")

    db.session.commit()
    return redirect(url_for('dashboard'))


# delete bill from database
@app.route('/deleteBill', methods=['POST'])
@login_required
def deleteBill():
    bill_id = request.form['billId']
    bill = Bill.query.filter_by(id=bill_id).first()
    db.session.delete(bill)
    db.session.commit()
    return redirect(url_for('dashboard'))


# split bill with other housemates
@app.route('/splitBill', methods=['POST'])
@login_required
def splitBill():
    bill_id = request.form['billId']
    bill = Bill.query.filter_by(id=bill_id).first() # get bill
    deets = bill.details # bill details

    user = User.query.filter_by(id=current_user.id).first()
    house = House.query.filter_by(id=user.home).first()
    housemates = User.query.filter_by(home=house.id).all() # get housemates
    selectedMate = []

    for mate in housemates: # get housemates selected for bill split
        if request.form.get(str(mate.id)):
            selectedMate.append(mate.id)
    
    if not selectedMate: # user selected no housemate for bill split
        flash("No housemate selected to split bill with.")
        return redirect(url_for('dashboard'))


    amount = bill.amount / (len(selectedMate))
    for i in selectedMate: # add new bill for each selected housemate to database
        db.session.add(Bill(amount, deets, i))

    db.session.delete(bill)
    db.session.commit()
    flash("Success split operation.")
    return redirect(url_for('dashboard'))


# leave house
@app.route('/leaveHouse', methods=['POST'])
@login_required
def leaveHouse():
    userid = current_user.id
    user = User.query.filter_by(id=userid).first()
    user.home = None
    db.session.commit()
    flash("Left house successfully")
    return redirect(url_for('dashboard'))


# join or create new house
@app.route('/joinHouse', methods=['POST'])
@login_required
def joinHouse():
    userid = current_user.id
    user = User.query.filter_by(id=userid).first()
    address = request.form['address']
    house = House.query.filter_by(address=address).first()

    if house: # if house already exists, join it
        user.home = house.id
        flash("Joined house successfully")

    else: # create new house
        new_house = House(address)
        db.session.add(new_house)
        db.session.commit()

        user.home = new_house.id
        flash("New house created successfully")
    
    db.session.commit()
    return redirect(url_for('dashboard'))


# send message
@app.route('/sendMessage', methods=['POST'])
@login_required
def sendMessage():
    userid = current_user.id
    user = User.query.filter_by(id=userid).first()
    messageDetails = (user.username + " : " + request.form['messageDetails'])
    recipient = request.form['recipient']
    recipient_list = []
    if (recipient == 'all-users'):
        house = House.query.filter_by(id=user.home).first()
        if house:
            housemates = User.query.filter_by(home=house.id).all()
        else:
            housemates = [user]
        
        for mate in housemates:
            if (mate.id != userid):
                recipient_list.append(mate.id)
    else:
        recipient_list = [recipient]

    for user in recipient_list:
        newMessage = Message(message=messageDetails, sender=userid, recipient=user)
        db.session.add(newMessage)
    
    db.session.commit()
    flash("Sent message successfully")
    return redirect(url_for('dashboard'))


# internal server error handling
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("error.html", url=request.path, statuscode='500')


# unknown page error handling
@app.errorhandler(404)
def page_not_found_error(error):
    return render_template("error.html", url=request.path, statuscode='404')