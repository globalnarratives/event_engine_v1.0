from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')

def admin_required(f):
    """Decorator to require admin role for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard.home'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            user.last_login = db.func.now()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.home'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/account')
@login_required
def account():
    """View account information"""
    return render_template('auth/account.html')

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'GET':
        return render_template('auth/change_password.html')
    
    # POST - handle password change
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validation
    if not current_password or not new_password or not confirm_password:
        flash('All password fields are required.', 'error')
        return render_template('auth/change_password.html')
    
    # Verify current password
    if not check_password_hash(current_user.password_hash, current_password):
        flash('Current password is incorrect.', 'error')
        return render_template('auth/change_password.html')
    
    # Check new passwords match
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return render_template('auth/change_password.html')
    
    # Check password length
    if len(new_password) < 8:
        flash('New password must be at least 8 characters.', 'error')
        return render_template('auth/change_password.html')
    
    # Update password
    current_user.password_hash = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.account'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error changing password: {str(e)}', 'error')
        return render_template('auth/change_password.html')