from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
import uuid
import os
from datetime import datetime, timedelta
import qrcode
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Admin password
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Simple in-memory storage for demo
users = {}
games = {}
challenges = [
    "Get another player to spell any word out loud.",
    "Get another player to yawn right after you do.",
    "Get another player to say \"thank you\" to you.",
    "Get another player to look up information for you on their phone.",
    "Get another player to correct an obviously false statement you make.",
    "Get another player to hold your phone for you.",
    "Get another player to give you a high-five.",
    "Get another player to ask \"What?\" after you say something to them.",
    "Get another player to agree with a ridiculous statement you make.",
    "Get another player to say they remember something from the past you bring up."
]

class User(UserMixin):
    def __init__(self, id, username, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

def generate_game_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Covert Agenda is running!'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('register'))
        
        # Check if username already exists
        for user in users.values():
            if user.username == username:
                flash('Username already exists')
                return redirect(url_for('register'))
        
        user_id = len(users) + 1
        user = User(user_id, username, generate_password_hash(password))
        users[user_id] = user
        
        login_user(user)
        flash('Registration successful!')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        for user in users.values():
            if user.username == username and check_password_hash(user.password_hash, password):
                login_user(user)
                flash('Login successful!')
                return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_games = [game for game in games.values() if current_user.id in game['players']]
    return render_template('dashboard.html', games=user_games)

@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        game_name = request.form['game_name'].strip()
        max_vetos = int(request.form.get('max_vetos', 3))
        
        if len(game_name) < 3:
            flash('Game name must be at least 3 characters long')
            return redirect(url_for('create_game'))
        
        game_code = generate_game_code()
        game_id = len(games) + 1
        
        games[game_id] = {
            'id': game_id,
            'name': game_name,
            'code': game_code,
            'admin_id': current_user.id,
            'players': [current_user.id],
            'max_vetos': max_vetos,
            'is_active': True,
            'created_at': datetime.now()
        }
        
        flash(f'Game created! Code: {game_code}')
        return redirect(url_for('game_room', game_id=game_id))
    
    return render_template('create_game.html')

@app.route('/join_game', methods=['GET', 'POST'])
@login_required
def join_game():
    if request.method == 'POST':
        game_code = request.form['game_code'].strip().upper()
        
        for game in games.values():
            if game['code'] == game_code and game['is_active']:
                if current_user.id not in game['players']:
                    game['players'].append(current_user.id)
                    flash('Successfully joined the game!')
                else:
                    flash('You are already in this game!')
                return redirect(url_for('game_room', game_id=game['id']))
        
        flash('Invalid game code or game not found')
        return redirect(url_for('join_game'))
    
    return render_template('join_game.html')

@app.route('/game/<int:game_id>')
@login_required
def game_room(game_id):
    game = games.get(game_id)
    if not game or current_user.id not in game['players']:
        flash('Game not found or you are not a player')
        return redirect(url_for('dashboard'))
    
    return render_template('game_room.html', game=game)

@app.route('/api/get_challenge/<int:game_id>')
@login_required
def get_challenge(game_id):
    game = games.get(game_id)
    if not game or current_user.id not in game['players']:
        return jsonify({'error': 'Game not found'}), 404
    
    challenge = random.choice(challenges)
    return jsonify({
        'challenge': challenge,
        'game_id': game_id
    })

@app.route('/api/complete_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def complete_challenge(challenge_id):
    game_id = request.json.get('game_id')
    game = games.get(game_id)
    if not game or current_user.id not in game['players']:
        return jsonify({'error': 'Game not found'}), 404
    
    return jsonify({'message': 'Challenge completed!'})

@app.route('/admin_login', methods=['POST'])
def admin_login():
    password = request.form.get('admin_password')
    if password == ADMIN_PASSWORD:
        session['is_admin'] = True
        flash('Admin access granted!')
        return redirect(url_for('admin_menu'))
    else:
        flash('Invalid admin password')
        return redirect(url_for('index'))

@app.route('/admin_menu')
def admin_menu():
    if not session.get('is_admin'):
        flash('Admin access required')
        return redirect(url_for('index'))
    return render_template('admin_menu.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 