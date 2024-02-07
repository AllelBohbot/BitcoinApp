from flask import Flask, render_template, jsonify, request
from flask_cors import cross_origin
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

bitcoin_values = []
last_average_time = None


def get_bitcoin_value():
    response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
    data = response.json()
    try:
        return data['bitcoin']['usd']
    except KeyError:
        print(f'Error: Could not find "bitcoin" key in the response data.')
        print(f'Response data: {data}')
        return None


def calculate_average():
    global last_average_time

    if len(bitcoin_values) == 0:
        return 0

    if last_average_time is None or (datetime.now() - last_average_time).total_seconds() >= 600:
        print(f'[{datetime.now()}] Time condition met for average calculation.')

        average_value = sum(bitcoin_values) / len(bitcoin_values)

        # Clear the values for the next interval
        bitcoin_values.clear()

        last_average_time = datetime.now()  # Update last_average_time

        return average_value
    else:
        print(f'[{datetime.now()}] Not yet time to calculate average.')

        return 0


@app.route('/service-a/get_bitcoin_value')
@cross_origin()
def get_bitcoin_value_endpoint():
    if request.path == '/service-a/get_bitcoin_value':
        current_value = get_bitcoin_value()

        # Append the value only if the time condition is not met
        if last_average_time is None or (datetime.now() - last_average_time).total_seconds() < 600:
            bitcoin_values.append(current_value)

        return jsonify({'current_value': current_value})
    else:
        return "Invalid path", 400


@app.route('/service-a/get_average_value')
@cross_origin()
def get_average_value_endpoint():
    average_value = calculate_average()
    return jsonify({'average_value': average_value})


@app.route('/service-a')
def index():
    current_value = get_bitcoin_value()

    # Print current value every minute
    print(f'[{datetime.now()}] Current Bitcoin Value: ${current_value}')

    global last_average_time
    if last_average_time is None or (datetime.now() - last_average_time).total_seconds() >= 600:
        # Print debug statement to see if the condition is met
        print(f'[{datetime.now()}] Time condition met for average calculation.')

        # Print average value every 2 minutes for debugging
        average_value = calculate_average()
        print(f'[{datetime.now()}] Average Bitcoin Value (Last 2 minutes): ${average_value}')

        # Reset the values for the next 2 minutes
        bitcoin_values.clear()
        last_average_time = datetime.now()
    else:
        print(f'[{datetime.now()}] Not yet time to calculate average.')

    return render_template('index.html', current_value=current_value)


# def sort(bitcoin_values):
#     for i in range(len(bitcoin_values)-1):
#         for j in range(i+1, len(bitcoin_values)):
#             if bitcoin_values[i] > bitcoin_values[j]:
#                 temp = bitcoin_values[i]
#                 bitcoin_values[i] = bitcoin_values[j]
#                 bitcoin_values[j] = temp
#     return bitcoin_values

# bitcoin_values = [4,8,6]


if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
