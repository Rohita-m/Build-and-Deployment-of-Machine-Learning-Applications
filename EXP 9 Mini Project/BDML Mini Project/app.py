from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

app = Flask(__name__)

app.config['SECRET_KEY'] = '1233444545555'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# --- Models ---

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(150),
        nullable=False
    )


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# --- Routes ---

@app.route('/')
def home():

    return render_template('home.html')


@app.route('/Register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        existing = User.query.filter_by(
            username=username
        ).first()

        if existing:

            flash(
                'User already exists',
                'error'
            )

            return redirect(
                url_for('register')
            )

        user = User(
            username=username,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        flash(
            'Registered successfully',
            'success'
        )

        return redirect(
            url_for('login')
        )

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            login_user(user)

            return redirect(
                url_for('dashboard')
            )

        flash(
            'Invalid credentials',
            'error'
        )

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    prediction_text = ""

    if request.method == 'POST':

        open_price = request.form['Open']
        high = request.form['High']
        low = request.form['Low']
        volume = request.form['Volume']

        # Dummy logic (replace with your ML model)

        predicted_price = (
            float(open_price)
            + float(high)
            + float(low)
        ) / 3

        prediction_text = (
            f"Predicted Stock Price: ₹{predicted_price:.2f}"
        )

    return render_template(
        'index.html',
        username=current_user.username,
        prediction_text=prediction_text
    )


@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(
        url_for('login')
    )


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)