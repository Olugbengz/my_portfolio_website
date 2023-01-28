from flask import Flask, render_template, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email
from datetime import date
import smtplib
import os


app = Flask(__name__)
app.secret_key = "@olu#Emma/gb4$ebg!a@"
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///subscribers.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


class RegForm(FlaskForm):
    email = StringField(label="", validators=[DataRequired(), Email(message='Kindly enter correct email.')],
                        render_kw={"placeholder": "Email"})
    submit = SubmitField("Register")


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
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


@app.route('/', methods=["GET", "POST"])
def home():
    email_form = RegForm()
    if email_form.validate_on_submit():
        new_subscriber = Subscriber(email=email_form.email.data)
        db.session.add(new_subscriber)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('index.html', form=email_form)


@app.route('/life_coaching')
def life_coach():
    email_form = RegForm()
    return render_template('life_coaching.html', form=email_form)


@app.route('/blog')
def blog_post():
    email_form = RegForm()
    return render_template('blog_post.html', form=email_form)


@app.route('/new_post')
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        add_new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            author=form.author.data,
            post_date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(add_new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)


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
            connection.sendmail(from_addr=sender_email, to_addrs=my_email, msg=f"Subject:{subject}\n\n{message}\n You can reach me via this Email:{sender_email}")
            return redirect(url_for('life_coach'))
    return render_template('contact.html', msg_form=message_form, form=email_form)


# @app.route('/registration_success')
# def submit_email():
#
#     return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

