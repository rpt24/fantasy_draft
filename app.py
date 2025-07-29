from flask import Flask, render_template, request, redirect, jsonify, session
import json
import os

app = Flask(__name__)
app.secret_key = '2025FantasyDraft'  # Change this to something strong

DATA_FILE = 'data.json'
PASSCODE = "2025FantasyDraft"

# Load or initialize data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    data = load_data()
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    return render_template('index.html', leaderboard=sorted_data)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        passphrase = request.form.get('passphrase')
        if passphrase == PASSCODE:
            session['admin'] = True
            return redirect('/admin')  # Redirect after setting session
        return render_template('admin.html', error="Incorrect passphrase.", authorized=False)

    if session.get('admin'):
        data = load_data()
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        return render_template('admin.html', leaderboard=sorted_data, authorized=True)

    return render_template('admin.html', authorized=False)


@app.route('/update', methods=['POST'])
def update():
    if not session.get('admin'):
        return "Unauthorized", 403

    data = load_data()
    action = request.form.get('action')
    name = request.form.get('name')

    try:
        if action == 'add':
            if name not in data:
                data[name] = 0
        elif action == 'remove':
            data.pop(name, None)
        elif action == 'increment':
            data[name] += 1
        elif action == 'decrement':
            data[name] -= 1
        save_data(data)
    except Exception as e:
        return str(e), 400

    return redirect('/admin', code=302)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

@app.route('/api/leaderboard')
def api_leaderboard():
    data = load_data()
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_data)

if __name__ == '__main__':
    #app.run(debug=True)
    port = int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0', port=port, debug=True)
