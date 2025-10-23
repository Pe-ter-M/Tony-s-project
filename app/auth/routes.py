from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, EditUserForm
from app.models.user import User, UserRole
from app import db
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        print(f"Login attempt - Username: {form.username.data}, Password: {form.password.data}")
        
        user = User.query.filter_by(username=form.username.data).first()
        print(f'user found {user}')
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            print("Login failed: Invalid credentials")
            return redirect(url_for('auth.login'))
        
        if not user.active:
            flash('Account is disabled', 'error')
            print("Login failed: Account disabled")
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.first_name}!', 'success')
        print(f"Login successful for user: {user.username}, Role: {user.role.value}")
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    print(f"User {current_user.username} logged out")
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/users')
@login_required
@admin_required
def user_management():
    """Admin page to view all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/user_management.html', users=users)

@bp.route('/register', methods=['GET', 'POST'])
# @login_required
# @admin_required
def register():
    """Admin endpoint to register new users"""
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('auth/register.html', form=form)
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email address already registered.', 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        new_user = User()
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=UserRole.ADMIN if form.role.data == 'admin' else UserRole.STAFF,
            active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} has been created successfully!', 'success')
        return redirect(url_for('auth.user_management'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Admin endpoint to edit user details"""
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    # Remove password requirement for editing
    form.password.validators = []
    form.confirm_password.validators = []
    
    if form.validate_on_submit():
        # Check if username already exists (excluding current user)
        existing_user = User.query.filter(
            User.username == form.username.data,
            User.id != user_id
        ).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('auth/edit_user.html', form=form, user=user)
        
        # Check if email already exists (excluding current user)
        existing_email = User.query.filter(
            User.email == form.email.data,
            User.id != user_id
        ).first()
        if existing_email:
            flash('Email address already registered.', 'error')
            return render_template('auth/edit_user.html', form=form, user=user)
        
        # Update user details
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role = UserRole.ADMIN if form.role.data == 'admin' else UserRole.STAFF
        user.active = form.is_active.data
        
        # Update password only if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        
        flash(f'User {user.username} has been updated successfully!', 'success')
        return redirect(url_for('auth.user_management'))
    
    return render_template('auth/edit_user.html', form=form, user=user)

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Admin endpoint to delete a user"""
    if current_user.id == user_id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('auth.user_management'))
    
    user = User.query.get_or_404(user_id)
    username = user.username
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted successfully!', 'success')
    return redirect(url_for('auth.user_management'))

@bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """Admin endpoint to activate/deactivate a user"""
    if current_user.id == user_id:
        return jsonify({'success': False, 'message': 'You cannot deactivate your own account.'})
    
    user = User.query.get_or_404(user_id)
    user.active = not user.active
    db.session.commit()
    
    action = 'activated' if user.active else 'deactivated'
    flash(f'User {user.username} has been {action} successfully!', 'success')
    return jsonify({
        'success': True, 
        'active': user.active,
        'message': f'User {action} successfully'
    })