
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import uuid
from sqlalchemy.dialects.postgresql import UUID

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirects to login page if not authenticated

# Define User model, representing each registered user
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Define Post model, representing a blog post
class Post(db.Model):
    __tablename__ = 'post'
    __table_args__ = {'extend_existing': True}
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

# This function helps Flask-Login find a user by their ID
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Home page route - displays all posts
@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

# Route to handle login requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Simple password check (for demonstration, not secure)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password!')
    return render_template('login.html')

# Route to log out the user and redirect to home
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Dashboard view for logged-in users to manage posts
@app.route('/dashboard')
@login_required
def dashboard():
    posts = Post.query.all()  # Get all posts
    return render_template('dashboard.html', posts=posts)  # Send to the dashboard template

# Route to display a single post based on its ID
@app.route('/post/<uuid:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# Route to edit an existing post
@app.route('/post/edit/<uuid:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Post updated successfully!')
        return redirect(url_for('post', post_id=post.id))
    return render_template('edit_post.html', post=post)

# Route to create a new post
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        flash('New post added successfully!')
        return redirect(url_for('post', post_id=new_post.id))
    return render_template('new_post.html')

# Route to delete an existing post
@app.route('/post/delete/<uuid:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!')
    return redirect(url_for('index'))

# Command to add a new user directly via the command line (useful for setting up an admin)
@app.cli.command('create_user')
def create_user_command():
    username = 'admin'
    password = 'admin'
    if User.query.filter_by(username=username).first() is None:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        print(f'User {username} added successfully.')
    else:
        print(f'User {username} already exists.')

# Main entry point - initializes database and starts the app
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()  # Set up database tables
    app.run(debug=True)
