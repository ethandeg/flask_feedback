from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserRegisterForm, LoginUserForm, FeedbackForm
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///flask_feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'abc123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserRegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(
            username, password, email=email, first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append(
                'Username take. Please pick another...')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)


@app.route('/secret')
def show_secret_route():
    if session['username']:
        return "You made it!"
    else:
        flash('Please login first', 'info')
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username=username, pwd=password)
        if user:
            session['username'] = user.username
            flash(f'Welcome Back {username}')
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('Goodbye!', 'info')
    return redirect('/')


@app.route('/users/<username>')
def show_user(username):
    if 'username' in session:
        user = User.query.filter_by(username=username).first()
        return render_template('user.html', user=user)
    else:
        flash('Please login first!', 'error')
        return redirect('/login')


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if session['username'] == username:
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
        flash(f'{username} succesfully deleted', 'info')
        return redirect('/')
    else:
        flash("You don't have permission to delete this user", 'error')
        return redirect(f'/users/{username}')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if session['username'] == username:
        form = FeedbackForm()
        user = User.query.filter_by(username=username).first()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(
                title=title, content=content, username=user.username)
            db.session.add(new_feedback)
            db.session.commit()
            return redirect(f'/users/{username}')
        else:
            return render_template('add_feedback.html', form=form, user=user)
    else:
        flash("You don't have permission to do that")
        return redirect(f'/users/{username}')


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if session['username'] == feedback.user.username:
        form = FeedbackForm()

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            flash(f"{feedback.title} was successfully updated!")
            db.session.commit()
            return redirect(f'/users/{feedback.user.username}')
        else:
            return render_template('update_feedback.html', form=form, feedback=feedback)
    else:
        flash("you don't have permission to do that")
        return redirect('/login')

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if session['username'] == feedback.user.username:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback successfully Deleted")
        return redirect(f'/users/{feedback.user.username}')
    else:
        flash("You don't have permission to do that")
        return redirect('/login')
        