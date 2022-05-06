from flask_login import UserMixin, LoginManager # user session management for Flask
from cwk import db
from werkzeug import security


class House(db.Model):
    __tablename__ = "houses"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), unique=True, nullable=False)
    tenants = db.relationship('User', backref='houses', lazy=True)

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return f'<House {self.id}>'


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    hashed_password = db.Column(db.String(100), nullable=False)
    home = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=True)
    debt = db.relationship('Bill', backref='users', lazy=True)

    def __init__(self, username, email, hashed_password, home):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.home = home

    def __repr__(self):
        return f'<User {self.id}>'


class Bill(db.Model):
    __tablename__ =  "bills"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float(), nullable=False)
    details = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

    def __init__(self, amount, details, person):
        self.amount = amount
        self.details = details
        self.user_id = person

    def __repr__(self):
        return f'<Bill {self.id}>'


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text(), nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

    def __init__(self, message, sender, recipient):
        self.message = message
        self.sender = sender
        self.user_id = recipient
    
    def __repr__(self):
        return f'<Message {self.id}>'




# dummy data
def dbinit():

    house_list = [
        House("sherbourne flat 53"),
        House("coventry")
        ]
    db.session.add_all(house_list)

    warwick = House.query.filter_by(address="sherbourne flat 53").first().id
    coventry = House.query.filter_by(address="coventry").first().id

    user_list = [
        User("Person1", "person1@email.com",security.generate_password_hash("test1"), warwick),
        User("Person2", "test2@a.com",security.generate_password_hash("test2"), warwick),
        User("Person3", "test3@a.com",security.generate_password_hash("test3"), None),
        User("Person4", "test4@a.com",security.generate_password_hash("test4"), warwick),
        User("Person5", "test5@a.com",security.generate_password_hash("test5"), None),
        User("Person6", "test6@a.com",security.generate_password_hash("test6"), coventry),

        ]
    db.session.add_all(user_list)

    fid = User.query.filter_by(username="Person1").first().id

    pid = User.query.filter_by(username="Person2").first().id

    listBill = [
        Bill(100, "Shopping", fid),
        Bill(200, "Chores", fid),
        Bill(300, "Work", fid),
        Bill(400, "Study", fid)
        ]
    db.session.add_all(listBill)



    db.session.commit()