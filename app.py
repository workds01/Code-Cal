from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roster.db'
db = SQLAlchemy(app)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_guest = db.Column(db.Boolean, default=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    caregiver = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'caregiver': self.caregiver,
            'notes': self.notes
        }

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Guest password - change this in production!
GUEST_PASSWORD = "ava2025"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('calendar'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('calendar'))
    return render_template('login.html')

@app.route('/guest-login', methods=['POST'])
def guest_login():
    password = request.form.get('password')
    if password == GUEST_PASSWORD:
        # Create or get guest user
        guest = User.query.filter_by(username='guest').first()
        if not guest:
            guest = User(
                username='guest',
                password_hash=generate_password_hash('not-used'),
                is_admin=False,
                is_guest=True
            )
            db.session.add(guest)
            db.session.commit()
        
        login_user(guest)
        return redirect(url_for('calendar'))
    
    flash('Invalid guest password')
    return redirect(url_for('login'))

@app.route('/admin-login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('calendar'))
    
    flash('Invalid username or password')
    return redirect(url_for('login'))

@app.route('/calendar')
@login_required
def calendar():
    schedules = Schedule.query.all()
    return render_template('calendar.html', schedules=[s.to_dict() for s in schedules])

@app.route('/edit_schedule', methods=['GET', 'POST'])
@login_required
def edit_schedule():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.')
        return redirect(url_for('calendar'))
    
    if request.method == 'POST':
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        caregiver = request.form.get('caregiver')
        notes = request.form.get('notes')
        
        schedule = Schedule.query.filter_by(date=date).first()
        if schedule:
            schedule.caregiver = caregiver
            schedule.notes = notes
        else:
            schedule = Schedule(date=date, caregiver=caregiver, notes=notes)
            db.session.add(schedule)
        
        db.session.commit()
        flash('Schedule updated successfully')
        return redirect(url_for('calendar'))
    
    return render_template('edit_schedule.html')

@app.route('/edit_schedule/<int:schedule_id>', methods=['POST'])
@login_required
def edit_schedule_entry(schedule_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.')
        return redirect(url_for('calendar'))
    
    schedule = Schedule.query.get_or_404(schedule_id)
    schedule.caregiver = request.form.get('caregiver')
    schedule.notes = request.form.get('notes')
    db.session.commit()
    
    flash('Schedule updated successfully')
    return redirect(url_for('calendar'))

@app.route('/delete_schedule/<int:schedule_id>')
@login_required
def delete_schedule(schedule_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.')
        return redirect(url_for('calendar'))
    
    schedule = Schedule.query.get_or_404(schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    
    flash('Schedule deleted successfully')
    return redirect(url_for('calendar'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def reset_db():
    """Drop all tables and recreate them"""
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_guest=False
        )
        db.session.add(admin)
        db.session.commit()

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_guest=False
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    reset_db()  # Reset database on startup
    app.run(debug=True)
