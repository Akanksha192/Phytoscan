from tensorflow.keras.models import load_model
import numpy as np
import cv2
import joblib
import os
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# Loadin trained models here:

custom_model = load_model('custom_cnn_model.h5')
vgg16_model = load_model('vgg16_feature_extractor.h5')
classifier = load_model('final_classifier_model.h5')
pca = joblib.load('pca_model.pkl')

IMG_SIZE = (150, 150)

# numeric labels into original name labels:
label_map = {
    0: 'Pepper__bell___Bacterial_spot',
    1: 'Pepper__bell___healthy',
    2: 'Potato___Early_blight',
    3: 'Potato___Late_blight',
    4: 'Tomato_Early_blight',
    5: 'Tomato_Leaf_Mold'
}

app.secret_key = 'thesecretkey' 

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']

        if file:
            if not os.path.exists('static'):
                os.makedirs('static')
            img_path = os.path.join('static', file.filename)
            file.save(img_path)

            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, IMG_SIZE)
            img = img / 255.0
            img = np.expand_dims(img, axis=0)

            try:
                custom_features = custom_model.predict(img)
                vgg16_features = vgg16_model.predict(img)
                vgg16_features_flat = vgg16_features.reshape((vgg16_features.shape[0], -1))
                vgg16_reduced = pca.transform(vgg16_features_flat)

                combined_features = np.concatenate((custom_features, vgg16_reduced), axis=1)

                # Predict
                prediction = classifier.predict(combined_features)
                predicted_class = np.argmax(prediction, axis=1)[0]
                predicted_label = label_map[predicted_class]

                # Assuming a confidence level is needed, here's a simple example:
                confidence = np.max(prediction) * 100  # Convert to percentage

                return jsonify({
                    'disease': predicted_label,
                    'confidence': round(confidence, 2)
                })

            except Exception as e:
                print("Error during prediction:", e)
                return jsonify({'error': 'Model could not retrieve result due to an internal error.'})

    return jsonify({'error': 'No file uploaded or invalid request.'})


@app.route('/')
def func():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/rewards')
def rewards():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('rewards.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')  


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        flash('Logged in successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
