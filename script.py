from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import roslibpy
import time
import math

app = Flask(__name__)
CORS(app)

client = None
cmd_vel = None

# ---------- HOME PAGE ----------
@app.route('/')
def home():
    return render_template('index.html')

# ---------- CONNECT TO ROS ----------
@app.route('/connect', methods=['POST'])
def connect():
    global client, cmd_vel

    data = request.json
    host = data['host']
    port = int(data['port'])

    try:
        client = roslibpy.Ros(host=host, port=port)
        client.run()

        cmd_vel = roslibpy.Topic(
            client,
            '/turtle1/cmd_vel',
            'geometry_msgs/Twist'
        )

        return jsonify({"status": "connected"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------- MOVE ----------
@app.route('/move', methods=['POST'])
def move():
    if not cmd_vel:
        return jsonify({"status": "not connected"}), 400

    data = request.json
    lin = data['linear']
    ang = data['angular']

    cmd_vel.publish(roslibpy.Message({
        'linear': {'x': lin, 'y': 0.0, 'z': 0.0},
        'angular': {'x': 0.0, 'y': 0.0, 'z': ang}
    }))

    return jsonify({"status": "ok"})

# ---------- FULL ROUND ----------
@app.route('/round', methods=['POST'])
def full_round():
    if not cmd_vel:
        return jsonify({"status": "not connected"}), 400

    angular_speed = 1.0
    linear_speed = 2.0
    duration = (2 * math.pi) / angular_speed
    start_time = time.time()

    while time.time() - start_time < duration:
        cmd_vel.publish(roslibpy.Message({
            'linear': {'x': linear_speed, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': angular_speed}
        }))
        time.sleep(0.05)

    # Stop after round
    cmd_vel.publish(roslibpy.Message({
        'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
    }))

    return jsonify({"status": "done"})

# ---------- STOP ----------
@app.route('/stop', methods=['POST'])
def stop():
    if not cmd_vel:
        return jsonify({"status": "not connected"}), 400

    cmd_vel.publish(roslibpy.Message({
        'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
    }))

    return jsonify({"status": "stopped"})

# ---------- RUN SERVER ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
