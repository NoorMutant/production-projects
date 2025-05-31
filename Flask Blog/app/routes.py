from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from app import db, bcrypt, mail
from app.models import User, Post
from app.forms import (
    RegistrationForm, LoginForm, UpdateAccountForm,
    PostForm, RequestResetForm, ResetPasswordForm, SearchForm
)
import os
import secrets
from PIL import Image
from datetime import datetime

# Create blueprints
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

# ----------------------
# Main Blueprint Routes
# ----------------------

@main.route("/")
@main.route("/home")
def home():
    try:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template("home.html", posts=posts)
    except Exception as e:
        error_message = f'An error occurred in home route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/about")
def about():
    try:
        return render_template("about.html")
    except Exception as e:
        error_message = f'An error occurred in about route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/admin/users")
@login_required
def admin_users():
    try:
        if current_user.has_admin_privileges():
            users = User.query.all()
            return render_template('admin_users.html', users=users)
        else:
            abort(403)
    except Exception as e:
        error_message = f'An error occurred in admin_users route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/admin/delete_post/<int:post_id>", methods=['POST'])
@login_required
def admin_delete_post(post_id):
    try:
        if current_user.has_admin_privileges():
            post = Post.query.get_or_404(post_id)
            db.session.delete(post)
            db.session.commit()
            flash('Post deleted successfully!', 'success')
            return redirect(url_for('main.admin_users'))
        else:
            abort(403)
    except Exception as e:
        error_message = f'An error occurred in admin_delete_post route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/admin/delete_user/<int:user_id>", methods=['POST'])
@login_required
def admin_delete_user(user_id):
    try:
        if current_user.has_admin_privileges():
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully!', 'success')
            return redirect(url_for('main.admin_users'))
        else:
            abort(403)
    except Exception as e:
        error_message = f'An error occurred in admin_delete_user route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/admin/posts")
@login_required
def admin_posts():
    try:
        if current_user.has_admin_privileges():
            posts = Post.query.all()
            return render_template('admin_posts.html', title='Admin Posts', posts=posts)
        else:
            abort(403)
    except Exception as e:
        error_message = f'An error occurred in admin_posts route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/admin/dashboard")
@login_required
def admin_dashboard():
    try:
        if current_user.has_admin_privileges():
            return render_template('admin_dashboard.html', title='Admin Dashboard')
        else:
            abort(403)
    except Exception as e:
        error_message = f'An error occurred in admin_dashboard route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/post/<int:post_id>")
def post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        image_url = url_for('static', filename='profile_pics/' + post.author.image_file)
        return render_template('post.html', title=post.title, post=post, image=image_url)
    except Exception as e:
        error_message = f'An error occurred in post route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)

        form = PostForm(obj=post)
        if form.validate_on_submit():
            form.populate_obj(post)
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('main.post', post_id=post.id))

        return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')
    except Exception as e:
        error_message = f'An error occurred in update_post route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('main.home'))
    except Exception as e:
        error_message = f'An error occurred in delete_post route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/user/<string:username>")
def user_posts(username):
    try:
        page = request.args.get('page', 1, type=int)
        user = User.query.filter_by(username=username).first_or_404()
        posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page, per_page=5)
        return render_template('user_posts.html', posts=posts, user=user)
    except Exception as e:
        error_message = f'An error occurred in user_posts route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@main.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()

    if form.validate_on_submit():
        search_term = form.search.data
        search_results = perform_search(search_term)

        if not search_results:
            flash(f'No results found for "{search_term}"', 'info')
        return render_template('search.html', title='Search Results', form=form, search_results=search_results)

    return render_template('search.html', title='Search', form=form)

def perform_search(search_term):
    matching_posts = Post.query.filter(
        (Post.title.ilike(f"%{search_term}%")) | (Post.content.ilike(f"%{search_term}%"))
    ).all()

    search_results = []

    for post in matching_posts:
        title_occurrences = post.title.lower().count(search_term.lower())
        content_occurrences = post.content.lower().count(search_term.lower())
        admin = post.author.username
        post_date = post.date_posted.strftime('%Y-%m-%d %H:%M:%S')

        search_results.append({
            'post_title': post.title,
            'title_occurrences': title_occurrences,
            'content_occurrences': content_occurrences,
            'admin': admin,
            'post_date': post_date,
            'id': post.id
        })

    return search_results

# ----------------------
# Auth Blueprint Routes
# ----------------------

@auth.route("/register", methods=['GET', 'POST'])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account is created, you can now login', 'success')
            return redirect(url_for('auth.login'))
        return render_template('register.html', title='Register', form=form)
    except Exception as e:
        error_message = f'An error occurred in register route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/login", methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
        return render_template('login.html', title='Login', form=form)
    except Exception as e:
        error_message = f'An error occurred in login route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/logout")
def logout():
    try:
        logout_user()
        return redirect(url_for('main.home'))
    except Exception as e:
        error_message = f'An error occurred in logout route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    try:
        form = UpdateAccountForm()

        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file

            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Account Updated', 'success')
            return redirect(url_for('auth.account'))

        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email

        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template("account.html", title='Account', image_file=image_file, form=form)
    except Exception as e:
        error_message = f'An error occurred in account route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    try:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.home'))
        return render_template('create_post.html', title='New Post', form=form, legend='New Post')
    except Exception as e:
        error_message = f'An error occurred in new_post route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        form = RequestResetForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('auth.login'))
        return render_template('reset_request.html', title='Reset Password', form=form)
    except Exception as e:
        error_message = f'An error occurred in reset_request route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        user = User.verify_reset_token(token)
        if user is None:
            flash('That is an invalid or expired token', 'warning')
            return redirect(url_for('auth.reset_request'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('auth.login'))
        return render_template('reset_token.html', title='Reset Password', form=form)
    except Exception as e:
        error_message = f'An error occurred in reset_token route: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

# Helper functions
def save_picture(form_picture):
    try:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

        output_size = (125, 125)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)

        return picture_fn
    except Exception as e:
        error_message = f'An error occurred in save_picture helper: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

def send_reset_email(user):
    try:
        token = user.get_reset_token()
        msg = Message('Password Reset Request',
                      sender='noreply@demo.com',
                      recipients=[user.email])
        msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request, please ignore this email.
'''
        mail.send(msg)
    except Exception as e:
        error_message = f'An error occurred in send_reset_email helper: {str(e)}'
        current_app.logger.error(error_message, exc_info=True)
        flash('Internal Server Error', 'danger')
        return redirect(url_for('main.home'))

# Error handlers
@main.errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404

@main.errorhandler(403)
def error_403(error):
    return render_template('403.html'), 403

@main.errorhandler(500)
def error_500(error):
    return render_template('500.html'), 500