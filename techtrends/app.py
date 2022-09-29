import sqlite3
import sys
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.db_con_count = app.db_con_count + 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.db_con_count = 0

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
    #   app.logger.info(f'Article with ID "{post_id}" not found!')
      app.logger.error(f'Article with ID "{post_id}" not found!')
      return render_template('404.html'), 404
    else:
      app.logger.info(f'Article "{post["title"]}" retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('"About Us"-page retrieved!')
    return render_template('about.html')

@app.route('/metrics')
def func_metrics():
    connection = get_db_connection()
    post_count = len(list(connection.execute('SELECT * FROM posts')))
    connection.close()
    
    result = {'db_connection_count': app.db_con_count,
    'post_count': post_count
    }
    app.logger.info('Metrics request successfull')
    return result, 200

@app.route('/healthz')
def func_healthz():
    result = {'result': 'OK - healthy'}
    app.logger.info('Health request successfull')
    return result, 200


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f'New Article "{title}" created!')
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    dual_handlers = [stdout_handler, stderr_handler]
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(asctime)s: %(message)s', handlers=dual_handlers)
    # logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
