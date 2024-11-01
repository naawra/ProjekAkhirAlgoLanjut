from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from urllib.parse import unquote
from flask_mysqldb import MySQL
import MySQLdb.cursors, re
import bcrypt

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'recipe'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

# Replace with your Spoonacular API key
API_KEY = 'b206cc27330c4515919f6f3816e7dfbe' #b206cc27330c4515919f6f3816e7dfbe

@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE username=%s",(username,))
        user = curl.fetchone()
        curl.close()
        
        if user is not None and len(user) > 0 :
            if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                session['loggedin'] = True
                session['id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('about'))
            else :
                flash("Gagal, Email dan Password Tidak Cocok")
                return redirect(url_for('login'))
        else : 
            flash("Gagal, User Tidak Ditemukan")
            return redirect(url_for('login'))
    else :
        return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else :
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password'].encode('utf-8')
            hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
            
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                flash("Account already exists!")
                return redirect(url_for('register'))
            elif not re.match(r'[A-Za-z0-9]+', username):
                flash("Username must contain only characters and numbers!")
                return redirect(url_for('register'))
            elif not username or not password or not username:
                flash("Please fill out the form!")
                return redirect(url_for('register'))
            else:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users (username,password) VALUES (%s, %s)",  (username, hash_password))
                mysql.connection.commit()
                session['username'] = request.form['username']
                return redirect(url_for('login'))

# Define the route for the "Home" button
@app.route('/home', methods=['GET'])
def home():
    # Check if user is logged in
    if 'loggedin' in session:
        # Render the main page with empty recipe list and search query
        return render_template('index.html', recipes=[], search_query='')
        # return render_template('home.html', name=session['name'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Remove session data and redirect to login page
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Define the main route for the app
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'loggedin' in session:
        if request.method == 'POST':
            # If a form is submitted
            query = request.form.get('search_query', '')
            # Perform a search for recipes with the given query
            recipes = search_recipes(query)
            # Render the main page with the search results and the search query
            return render_template('index.html', recipes=recipes, search_query=query)
        
        # If it's a GET request or no form submitted
        search_query = request.args.get('search_query', '')
        decoded_search_query = unquote(search_query)
        # Perform a search for recipes with the decoded search query
        recipes = search_recipes(decoded_search_query)
        # Render the main page
        return render_template('index.html', recipes=recipes, search_query=decoded_search_query)
    else:
        return redirect(url_for('login'))


# Function to search for recipes based on the provided query
def search_recipes(query):
    if 'loggedin' in session:
        url = f'https://api.spoonacular.com/recipes/complexSearch'
        params = {
            'apiKey': API_KEY,
            'query': query,
            'number': 6,
            'instructionsRequired': True,
            'addRecipeInformation': True,
            'fillIngredients': True,
        }

        # Send a GET request to the Spoonacular API with the query parameters
        response = requests.get(url, params=params)
        # If the API call is successful
        if response.status_code == 200:
            # Parse the API response as JSON data
            data = response.json()
            recipes = data['results']

            # Return the list of recipe results
            return recipes
        # If the API call is not successful
        return []
    else:
        return redirect(url_for('login'))
    
@app.route('/bookmark')
def bookmark():
    if 'loggedin' in session:
        id_user = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT recipe_id FROM bookmark WHERE id_user=%s", (id_user,))
        bookmarks = cursor.fetchall()
        recipes = []
        for bookmark in bookmarks:
            recipe_id = bookmark['recipe_id']
            url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
            params = {
                'apiKey': API_KEY,
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                recipe = response.json()
                recipes.append(recipe)
        return render_template('bookmark.html', recipes=recipes)
    else:
        return redirect(url_for('login'))
    
@app.route('/simpan', methods=['GET'])
def simpan():
    if 'loggedin' in session:
        recipe_id = request.args.get('recipe_id')
        user_id = session['id']
        if recipe_id is not None:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM bookmark WHERE id_user=%s AND recipe_id=%s", (user_id, recipe_id))
            bookmark = cursor.fetchone()
            if bookmark:
                flash("Recipe sudah disimpan")
                return redirect(url_for('home'))
            else:
                cursor.execute("INSERT INTO bookmark (id_user, recipe_id) VALUES (%s, %s)", (user_id, recipe_id))
                mysql.connection.commit()
                flash("Recipe berhasil disimpan")
                return redirect(url_for('bookmark'))
        else:
            flash("Recipe gagal disimpan")
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    
@app.route('/hapus', methods=['GET'])
def hapus():
    if 'loggedin' in session:
        recipe_id = request.args.get('recipe_id')
        user_id = session['id']
        if recipe_id is not None:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM bookmark WHERE id_user=%s AND recipe_id=%s", (user_id, recipe_id))
            bookmark = cursor.fetchone()
            if bookmark:
                cursor.execute("DELETE FROM bookmark WHERE id_user=%s AND recipe_id=%s", (user_id, recipe_id))
                mysql.connection.commit()
                return redirect(url_for('bookmark'))
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('about'))
    else:
        return redirect(url_for('login'))
        
# Route to view a specific recipe with a given recipe ID
@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    if 'loggedin' in session:
        # Get the search query from the URL query parameters
        search_query = request.args.get('search_query', '')
        # Build the URL to get information about the specific recipe ID from Spoonacular API
        url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
        params = {
            'apiKey': API_KEY,
        }

        # Send a GET request to the Spoonacular API to get the recipe information
        response = requests.get(url, params=params)
        # If the API call is successful
        if response.status_code == 200:
            recipe = response.json()
            return render_template('recipePage.html', recipe=recipe, search_query=search_query)
        return "Recipe not found", 404
    else:
        return redirect(url_for('login'))
    
@app.route('/apn')
def dash():
    return render_template('dash/index.html')

# Run the app in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)