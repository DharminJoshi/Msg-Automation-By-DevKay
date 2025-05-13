from flask import Flask, request, jsonify
from flask_cors import CORS
from responder import DevKaySmartResponder  # Your existing responder class

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow requests from your mobile app

# Initialize the responder
responder = DevKaySmartResponder()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "DevKay Smart Responder API is running."})

@app.route("/respond", methods=["POST"])
def respond():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' in request"}), 400

        user_message = data["message"]
        reply = responder.generate_and_log_response(user_message)

        return jsonify({"reply": reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
