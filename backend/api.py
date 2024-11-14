from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Your route definitions

@app.route('/api/travel', methods=['POST'])
def travel_agent():
    data = request.get_json()
    departure_airport = data.get('departure_airport')
    destination_airport = data.get('destination_airport')
    number_of_people = data.get('number_of_people')
    budget_range = data.get('budget_range')
    departure_date = data.get('departure_date')
    return_date = data.get('return_date')

    response = {
        "status": "success",
        "message": "Travel details received",
        "details": {
            "departure_airport": departure_airport,
            "destination_airport": destination_airport,
            "number_of_people": number_of_people,
            "budget_range": budget_range,
            "departure_date": departure_date,
            "return_date": return_date,
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
