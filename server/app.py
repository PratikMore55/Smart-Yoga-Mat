from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained model and label encoder
model = joblib.load("yoga_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

@app.route("/", methods=["GET"])
def home():
    return "Yoga AI Model API is running."

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        input_data = np.array(data["features"]).reshape(1, -1)  # Ensure it's the correct shape
        prediction = model.predict(input_data)[0]
        result = label_encoder.inverse_transform([prediction])[0]
        return jsonify({"prediction": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
