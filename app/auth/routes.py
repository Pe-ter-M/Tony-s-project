from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.auth.forms import LoginForm
from app.models.user import User
from app import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already authenticated, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Print form data for debugging
        print(f"Login attempt - Username: {form.username.data}, Password: {form.password.data}")
        
        user = User.query.filter_by(username=form.username.data).first()
        print(f'user found {user}')
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            print("Login failed: Invalid credentials")
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Account is disabled', 'error')
            print("Login failed: Account disabled")
            return redirect(url_for('auth.login'))
        
        # Login successful
        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.first_name}!', 'success')
        print(f"Login successful for user: {user.username}, Role: {user.role.value}")
        
        # Redirect to next page or dashboard
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