from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from werkzeug.security import generate_password_hash
from app.models import User
from app import db
from app.routes.auth import admin_required
import secrets
import string

bp = Blueprint('admin', __name__, url_prefix='/admin')

def generate_temp_password(length=12):
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))

@bp.route('/users')
@admin_required
def users():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create a new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role', 'analyst')
        
        # Validation
        if not username or not email:
            flash('Username and email are required.', 'error')
            return render_template('admin/create_user.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'error')
            return render_template('admin/create_user.html')
        
        if User.query.filter_by(username=username).first():
            flash('A user with this username already exists.', 'error')
            return render_template('admin/create_user.html')
        
        # Generate temporary password
        temp_password = generate_temp_password()
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(temp_password),
            role=role,
            is_active=True
        )
        
        db.session.add(user)
        
        try:
            db.session.commit()
            flash(f'User created successfully! Temporary password: {temp_password}', 'success')
            flash('Please save this password - it will not be shown again.', 'warning')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
    
    return render_template('admin/create_user.html')

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user details"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from editing their own role or deactivating themselves
    is_self = (user.id == current_user.id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        is_active = 'is_active' in request.form
        new_password = request.form.get('new_password')
        
        # Validation
        if not username or not email:
            flash('Username and email are required.', 'error')
            return render_template('admin/edit_user.html', user=user, is_self=is_self)
        
        # Check for duplicate username (excluding current user)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('A user with this username already exists.', 'error')
            return render_template('admin/edit_user.html', user=user, is_self=is_self)
        
        # Check for duplicate email (excluding current user)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash('A user with this email already exists.', 'error')
            return render_template('admin/edit_user.html', user=user, is_self=is_self)
        
        # Prevent admin from deactivating themselves
        if is_self and not is_active:
            flash('You cannot deactivate your own account.', 'error')
            return render_template('admin/edit_user.html', user=user, is_self=is_self)
        
        # Prevent admin from changing their own role
        if is_self and role != user.role:
            flash('You cannot change your own role.', 'error')
            return render_template('admin/edit_user.html', user=user, is_self=is_self)
        
        # Update user
        user.username = username
        user.email = email
        user.role = role
        user.is_active = is_active
        
        # Update password if provided
        if new_password:
            user.password_hash = generate_password_hash(new_password)
            flash('Password updated successfully.', 'success')
        
        try:
            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')
    
    return render_template('admin/edit_user.html', user=user, is_self=is_self)

@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_password(user_id):
    """Reset user password to a new temporary password"""
    user = User.query.get_or_404(user_id)
    
    # Generate new temporary password
    temp_password = generate_temp_password()
    user.password_hash = generate_password_hash(temp_password)
    
    try:
        db.session.commit()
        flash(f'Password reset successfully! New temporary password: {temp_password}', 'success')
        flash('Please save this password - it will not be shown again.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting password: {str(e)}', 'error')
    
    return redirect(url_for('admin.edit_user', user_id=user_id))

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user (soft delete via deactivation recommended)"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    # Soft delete - just deactivate
    user.is_active = False
    
    try:
        db.session.commit()
        flash(f'User {user.username} has been deactivated.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deactivating user: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))