from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import joblib
import os

app = Flask(__name__)
app.secret_key = 'thesecretkey' 
classifier = load_model('final_classifier_model.h5')
pca = joblib.load('pca_model.pkl')
IMG_SIZE = (150, 150)
label_map = {
    0: 'Pepper__bell___Bacterial_spot',
    1: 'Pepper__bell___healthy',
    2: 'Potato___Early_blight',
    3: 'Potato___Late_blight',
    4: 'Tomato_Early_blight',
    5: 'Tomato_Leaf_Mold'
}

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '9090Root#',
    'database': 'groot_db'
}


def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

from flask import session, redirect, url_for, flash

@app.route('/')
def success():
    if 'username' in session:
        return f"Hello, {session['username']}! <br><a href='/logout'>Logout</a>" + render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            flash('Username or email already exists.', 'danger')
            cursor.close()
            conn.close()
            return render_template('signup.html')

        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/action')
def action():
    return render_template('action.html')

@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/report')
def report():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('report.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/impact')
def impact():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    username = session['username']
    
    impact = get_impact_for_user(username)

    if impact is None:
        impact = {
            'carbon_saved': 0,
            'water_conserved': 0,
            'waste_reduced': 0,
            'actions_completed': 0
        }
    
    return render_template('impact.html', impact=impact)

@app.route('/rewards')
def rewards():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('rewards.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
from flask import jsonify

def get_impact_for_user(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM impact_users WHERE username = %s", (username,))
    impact = cursor.fetchone()
    cursor.close()
    conn.close()
    return impact

def create_impact_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO impact_users (username) VALUES (%s)", (username,))
    conn.commit()
    cursor.close()
    conn.close()

def update_impact_user(username, carbon_saved, water_conserved, waste_reduced, actions_completed):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM impact_users WHERE username = %s", (username,))
    exists = cursor.fetchone()
    if not exists:
        create_impact_user(username)
    
    cursor.execute("""
        UPDATE impact_users SET 
            carbon_saved = carbon_saved + %s,
            water_conserved = water_conserved + %s,
            waste_reduced = waste_reduced + %s,
            actions_completed = actions_completed + %s
        WHERE username = %s
    """, (carbon_saved, water_conserved, waste_reduced, actions_completed, username))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/impact/update', methods=['POST'])
def impact_update():
    if 'username' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.form
    username = session['username']

    try:
        carbon_saved = float(data.get('carbon_saved', 0))
        water_conserved = float(data.get('water_conserved', 0))
        waste_reduced = float(data.get('waste_reduced', 0))
        actions_completed = int(data.get('actions_completed', 0))

        if min(carbon_saved, water_conserved, waste_reduced, actions_completed) < 0:
            return jsonify({'error': 'Values must be non-negative'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid input values'}), 400

    update_impact_user(username, carbon_saved, water_conserved, waste_reduced, actions_completed)
    updated_impact = get_impact_for_user(username)
    return jsonify({
        'message': 'Impact updated successfully',
        'impact': updated_impact
    })

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']

        if file:
            img_path = os.path.join('static', file.filename)
            file.save(img_path)

            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, IMG_SIZE)
            img = img / 255.0
            img = np.expand_dims(img, axis=0)

            # Feature extraction like in training
            # Extract custom CNN features
            custom_features = custom_model.predict(img)

            # Extract VGG16 features
            vgg16_features = vgg16_model.predict(img)

            # Apply PCA on VGG16 features
            vgg16_reduced = pca.transform(vgg16_features)

            # Concatenate features
            combined_features = np.concatenate((custom_features, vgg16_reduced), axis=1)

            # Predict
            prediction = classifier.predict(combined_features)
            predicted_class = np.argmax(prediction, axis=1)[0]
            predicted_label = label_map[predicted_class]

            return render_template('result.html', label=predicted_label, img_path=img_path)

    return 'Something went wrong'

from markupsafe import Markup

@app.route('/impact')
def impact_enhanced():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    username = session['username']
    impact = get_impact_for_user(username)

    if not impact:
        impact = {
            'carbon_saved': 0,
            'water_conserved': 0,
            'waste_reduced': 0,
            'actions_completed': 0
        }

    base_content = render_template('impact.html')
    form_html = f'''
    <h3>Your Impact Stats</h3>
    <ul>
      <li>Carbon Saved: {impact['carbon_saved']:.2f} kg</li>
      <li>Water Conserved: {impact['water_conserved']:.2f} liters</li>
      <li>Waste Reduced: {impact['waste_reduced']:.2f} kg</li>
      <li>Actions Completed: {impact['actions_completed']}</li>
    </ul>

    <h3>Update Your Impact</h3>
    <form id="impactForm" method="post" action="/impact/update">
      <label>Carbon Saved (kg): <input type="number" step="0.01" name="carbon_saved" min="0" value="0" required></label><br>
      <label>Water Conserved (liters): <input type="number" step="0.01" name="water_conserved" min="0" value="0" required></label><br>
      <label>Waste Reduced (kg): <input type="number" step="0.01" name="waste_reduced" min="0" value="0" required></label><br>
      <label>Actions Completed: <input type="number" name="actions_completed" min="0" value="0" required></label><br>
      <button type="submit">Add Impact</button>
    </form>

    <div id="resultMessage"></div>

    <script>
        const form = document.getElementById('impactForm');
        form.addEventListener('submit', async function(e) {{
            e.preventDefault();

            let formData = new FormData(form);
            const response = await fetch(form.action, {{
                method: 'POST',
                body: formData,
            }});

            const data = await response.json();
            const resultDiv = document.getElementById('resultMessage');

            if (response.ok) {{
                let impact = data.impact;
                resultDiv.style.color = 'green';
                resultDiv.innerHTML = data.message + '<br>' +
                    `<ul>
                        <li>Carbon Saved: ${impact.carbon_saved.toFixed(2)} kg</li>
                        <li>Water Conserved: ${impact.water_conserved.toFixed(2)} liters</li>
                        <li>Waste Reduced: ${impact.waste_reduced.toFixed(2)} kg</li>
                        <li>Actions Completed: ${impact.actions_completed}</li>
                    </ul>`;
            }} else {{
                resultDiv.style.color = 'red';
                resultDiv.textContent = data.error || 'Error updating impact.';
            }}
        }});
    </script>
    '''
if __name__ == '__main__':
    app.run(debug=True)