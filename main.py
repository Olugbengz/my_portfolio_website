import flask
from flask import Flask, render_template, url_for, redirect, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, URL
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import smtplib
import os


app = Flask(__name__)
app.secret_key = "MY_SECRET_KEY"
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///subscribers.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog_posts"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///comments"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


#Tables
class Subscriber(db.Model):
    __tablename__ = "subscribers"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


class Comment(db.Model):
    __tablename__ = "comments"
    d = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)


# with app.app_context():
#     db.create_all()
# Forms


class RegForm(FlaskForm):
    email = StringField(label="", validators=[DataRequired(), Email(message='Kindly enter correct email.')],
                        render_kw={"placeholder": "Email"})
    submit = SubmitField("Register")


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired(), URL()])
    image = StringField('Image URL', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    submit = SubmitField('Create Post')


class MessageForm(FlaskForm):
    name = StringField(label="", validators=[DataRequired()], render_kw={"placeholder": "Full Name"})
    email = StringField(label="", validators=[DataRequired(), Email(message='Kindly enter correct email.')],
                        render_kw={"placeholder": "Email"})
    subject = StringField(label="", validators=[DataRequired()], render_kw={"placeholder": "Subject"})
    body = TextAreaField(label="", validators=[DataRequired()], render_kw={"placeholder": "Message"})
    submit = SubmitField("Send Message")


class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class UserRegForm(FlaskForm):
    name = StringField(label='Full Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField('Register')


@app.route('/', methods=["GET", "POST"])
def home():
    email_form = RegForm()
    if email_form.validate_on_submit():
        new_subscriber = Subscriber(email=email_form.email.data)
        db.session.add(new_subscriber)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('index.html', form=email_form, authenticated_user=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register():
    email_form = RegForm()
    account_form = UserRegForm()
    if account_form.validate_on_submit():
        if User.query.filter_by(email=account_form.email.data).first():
            flash("You've already signed up with that email, log in instead!", category="error")
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password=account_form.password.data, method="pbkdf2:sha256",
                                                 salt_length=16)
        new_acc = User(
            name=account_form.name.data,
            email=account_form.email.data,
            password=hashed_password
        )
        db.session.add(new_acc)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', reg_form=account_form, form=email_form,
                           authenticated_user=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    email_form = RegForm()
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flask.flash("Your email seems incorrect, please try again.", category="error")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', category="error")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('blog_post'))
    return render_template("login.html", login_form=login_form, authenticated_user=current_user.is_authenticated,
                           form=email_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/life_coaching')
def life_coach():
    email_form = RegForm()
    return render_template('life_coaching.html', form=email_form, authenticated_user=current_user.is_authenticated)


@app.route('/new_post', methods=['GET', 'POST'])
def create_post():
    new_post_form = CreatePostForm()
    email_form = RegForm()
    if new_post_form.validate_on_submit():
        add_new_post = BlogPost(
            title=new_post_form.title.data,
            subtitle=new_post_form.subtitle.data,
            body=new_post_form.body.data,
            img_url=new_post_form.image.data,
            author=new_post_form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(add_new_post)
        db.session.commit()
        return redirect(url_for('blog_post'))
    return render_template('create_post.html', form=email_form, blog_form=new_post_form,
                           authenticated_user=current_user.is_authenticated)


@app.route('/blog', methods=['GET', 'POST'])
def blog_post():
    email_form = RegForm()
    posts = BlogPost.query.all()
    return render_template('blog_post.html', all_posts=posts, form=email_form,
                           authenticated_user=current_user.is_authenticated)


@app.route('/blog/<int:post_id>', methods=["GET", "POST"])
def display_post(post_id):
    email_form = RegForm()
    request_post = BlogPost.query.get(post_id)
    return render_template('display_post.html', form=email_form, post=request_post,
                           authenticated_user=current_user.is_authenticated)


@app.route('/contact', methods=["GET", "POST"])
def contact_me():
    email_form = RegForm()
    message_form = MessageForm()
    if message_form.validate_on_submit():
        sender_email = message_form.email.data
        subject = message_form.subject.data
        message = message_form.body.data
        my_email = os.environ['MY_EMAIL']
        password = os.environ['MY_PASSWORD']

        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.ehlo()
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=sender_email, to_addrs=my_email,
                                msg=f"Subject:{subject}\n\n{message}\n You can reach me via this Email:{sender_email}")

            return redirect(url_for('life_coach'))
    return render_template('contact.html', msg_form=message_form, form=email_form,
                           authenticated_user=current_user.is_authenticated)


# @app.route('/registration_success')
# def submit_email():
#
#     return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

