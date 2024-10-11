from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import requests
import json
import random

app = Flask(__name__)
app.secret_key = "123456"

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

blog_posts = []
API_KEY = "aFqgb77k1nTty6HyrowYK0a6XLP0XnV6YOEw5LUr"  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cars', methods=['GET'])
def cars():
    make = request.args.get('make')
    model = request.args.get('search')  
    limit = 10  

    url = 'https://api.api-ninjas.com/v1/cars'
    params = {}
    if make:
        params['make'] = make
    if model:
        params['model'] = model
    params['limit'] = limit

    if not make and not model:
        random_makes = ['Toyota', 'Ford', 'Honda', 'BMW', 'Chevrolet', 'Nissan']
        random_make = random.choice(random_makes)  
        params['make'] = random_make  

    response = requests.get(url, headers={'X-Api-Key': API_KEY}, params=params)

    if response.status_code != 200:
        flash('Failed to retrieve car data. Please try again later.')
        return render_template('index.html', cars=[])

    try:
        car_data = response.json()
    except json.JSONDecodeError:
        flash('Received invalid data from the API. Please try again later.')
        return render_template('index.html', cars=[])

    random.shuffle(car_data)  
    car_data = car_data[:10]  

    return render_template('index.html', cars=car_data)

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    form = BlogForm()
    if form.validate_on_submit():
        if 'username' in session and session['username'] == 'admin@admin.is':  
            post = {
                'title': form.title.data,
                'content': form.content.data
            }
            blog_posts.append(post)
            return redirect(url_for('blog'))
        else:
            flash('You must be logged in as admin to post blog entries.')

    return render_template('blog.html', form=form, posts=blog_posts, is_admin='username' in session and session['username'] == 'admin@admin.is')

@app.route('/delete_post/<int:index>', methods=['POST'])
def delete_post(index):
    if 'username' in session and session['username'] == 'admin@admin.is':
        if 0 <= index < len(blog_posts):  # Check if the index is valid
            blog_posts.pop(index)  # Remove the post at the given index
            flash('Post deleted successfully!')
        else:
            flash('Post not found.')
    else:
        flash('You must be logged in as admin to delete blog entries.')
    return redirect(url_for('blog'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin@admin.is' and password == '123456':
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
