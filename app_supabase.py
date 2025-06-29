from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from supabase.client import create_client, Client
import random
import uuid
import os
from datetime import datetime, timedelta
import qrcode
import io
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://vqlmpgnzuhttzssuppkw.supabase.co')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxbG1wZ256dWh0dHpzc3VwcGt3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExODcyNjYsImV4cCI6MjA2Njc2MzI2Nn0.XoRv990NNt4q-VkGE6cZ8m3WJu6pHKXLjHC_OZMTzRI')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Admin password - you can change this
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash, is_admin=False, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at

    @staticmethod
    def get(user_id):
        """Get user by ID from Supabase"""
        try:
            response = supabase.table('users').select('*').eq('id', user_id).execute()
            if response.data:
                user_data = response.data[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    is_admin=user_data.get('is_admin', False),
                    created_at=user_data.get('created_at')
                )
        except Exception as e:
            print(f"Error getting user: {e}")
        return None

    @staticmethod
    def get_by_username(username):
        """Get user by username from Supabase"""
        try:
            response = supabase.table('users').select('*').eq('username', username).execute()
            if response.data:
                user_data = response.data[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    is_admin=user_data.get('is_admin', False),
                    created_at=user_data.get('created_at')
                )
        except Exception as e:
            print(f"Error getting user by username: {e}")
        return None

    @staticmethod
    def create(username, password_hash):
        """Create new user in Supabase"""
        try:
            response = supabase.table('users').insert({
                'username': username,
                'password_hash': password_hash,
                'is_admin': False
            }).execute()
            if response.data:
                user_data = response.data[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    is_admin=user_data.get('is_admin', False),
                    created_at=user_data.get('created_at')
                )
        except Exception as e:
            print(f"Error creating user: {e}")
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))

# Game class for managing games
class Game:
    def __init__(self, id, name, code, admin_password, is_active=True, winner_id=None, 
                 game_mode='open_ended', time_limit=None, target_challenges=None, max_vetos=3, created_at=None):
        self.id = id
        self.name = name
        self.code = code
        self.admin_password = admin_password
        self.is_active = is_active
        self.winner_id = winner_id
        self.game_mode = game_mode
        self.time_limit = time_limit
        self.target_challenges = target_challenges
        self.max_vetos = max_vetos
        self.created_at = created_at

    @staticmethod
    def get(game_id):
        """Get game by ID from Supabase"""
        try:
            response = supabase.table('games').select('*').eq('id', game_id).execute()
            if response.data:
                game_data = response.data[0]
                return Game(
                    id=game_data['id'],
                    name=game_data['name'],
                    code=game_data['code'],
                    admin_password=game_data['admin_password'],
                    is_active=game_data.get('is_active', True),
                    winner_id=game_data.get('winner_id'),
                    game_mode=game_data.get('game_mode', 'open_ended'),
                    time_limit=game_data.get('time_limit'),
                    target_challenges=game_data.get('target_challenges'),
                    max_vetos=game_data.get('max_vetos', 3),
                    created_at=game_data.get('created_at')
                )
        except Exception as e:
            print(f"Error getting game: {e}")
        return None

    @staticmethod
    def get_by_code(code):
        """Get game by code from Supabase"""
        try:
            response = supabase.table('games').select('*').eq('code', code).eq('is_active', True).execute()
            if response.data:
                game_data = response.data[0]
                return Game(
                    id=game_data['id'],
                    name=game_data['name'],
                    code=game_data['code'],
                    admin_password=game_data['admin_password'],
                    is_active=game_data.get('is_active', True),
                    winner_id=game_data.get('winner_id'),
                    game_mode=game_data.get('game_mode', 'open_ended'),
                    time_limit=game_data.get('time_limit'),
                    target_challenges=game_data.get('target_challenges'),
                    max_vetos=game_data.get('max_vetos', 3),
                    created_at=game_data.get('created_at')
                )
        except Exception as e:
            print(f"Error getting game by code: {e}")
        return None

    @staticmethod
    def create(name, admin_password, game_mode='open_ended', time_limit=None, target_challenges=None, max_vetos=3):
        """Create new game in Supabase"""
        try:
            code = generate_game_code()
            game_data = {
                'name': name,
                'code': code,
                'admin_password': admin_password,
                'game_mode': game_mode,
                'time_limit': time_limit,
                'target_challenges': target_challenges,
                'max_vetos': max_vetos,
                'is_active': True
            }
            
            response = supabase.table('games').insert(game_data).execute()
            if response.data:
                game_data = response.data[0]
                return Game(
                    id=game_data['id'],
                    name=game_data['name'],
                    code=game_data['code'],
                    admin_password=game_data['admin_password'],
                    is_active=game_data.get('is_active', True),
                    winner_id=game_data.get('winner_id'),
                    game_mode=game_data.get('game_mode', 'open_ended'),
                    time_limit=game_data.get('time_limit'),
                    target_challenges=game_data.get('target_challenges'),
                    max_vetos=game_data.get('max_vetos', 3),
                    created_at=game_data.get('created_at')
                )
        except Exception as e:
            print(f"Error creating game: {e}")
        return None

    def get_players(self):
        """Get all players in this game"""
        try:
            response = supabase.table('players').select('*, users(*)').eq('game_id', self.id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting players: {e}")
            return []

    def add_player(self, user_id):
        """Add player to game"""
        try:
            response = supabase.table('players').insert({
                'game_id': self.id,
                'user_id': user_id
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error adding player: {e}")
            return None

    def get_completed_challenges(self, user_id):
        """Get completed challenges for a user in this game"""
        try:
            response = supabase.table('completed_challenges').select('*').eq('game_id', self.id).eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting completed challenges: {e}")
            return []

    def complete_challenge(self, user_id, challenge_id):
        """Mark a challenge as completed"""
        try:
            response = supabase.table('completed_challenges').insert({
                'game_id': self.id,
                'user_id': user_id,
                'challenge_id': challenge_id
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error completing challenge: {e}")
            return None

    def get_vetoes(self, user_id):
        """Get vetoes for a user in this game"""
        try:
            response = supabase.table('vetoes').select('*').eq('game_id', self.id).eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting vetoes: {e}")
            return []

    def veto_challenge(self, user_id, challenge_id):
        """Veto a challenge"""
        try:
            response = supabase.table('vetoes').insert({
                'game_id': self.id,
                'user_id': user_id,
                'challenge_id': challenge_id
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error vetoing challenge: {e}")
            return None

    def end_game(self, winner_id=None):
        """End the game"""
        try:
            update_data = {'is_active': False}
            if winner_id:
                update_data['winner_id'] = winner_id
            
            response = supabase.table('games').update(update_data).eq('id', self.id).execute()
            if response.data:
                self.is_active = False
                self.winner_id = winner_id
            return response.data
        except Exception as e:
            print(f"Error ending game: {e}")
            return None

# Challenge class
class Challenge:
    @staticmethod
    def get_random():
        """Get a random challenge from Supabase"""
        try:
            response = supabase.table('challenges').select('*').execute()
            if response.data:
                return random.choice(response.data)
        except Exception as e:
            print(f"Error getting random challenge: {e}")
        return None

    @staticmethod
    def get_by_id(challenge_id):
        """Get challenge by ID"""
        try:
            response = supabase.table('challenges').select('*').eq('id', challenge_id).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            print(f"Error getting challenge by ID: {e}")
        return None

# Utility functions
def generate_game_code():
    """Generate a random 6-character game code"""
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

def get_random_challenge():
    """Get a random challenge"""
    return Challenge.get_random()

# Sample challenges for initialization
SAMPLE_CHALLENGES = [
    "Make someone laugh out loud",
    "Find something blue and show it to the group",
    "Tell a joke that makes at least 2 people smile",
    "Do your best impression of a famous person",
    "Share an interesting fact that no one else knows",
    "Make a funny face and hold it for 10 seconds",
    "Tell a story from your childhood in under 30 seconds",
    "Find something in the room that starts with the letter 'S'",
    "Do a dance move that makes people smile",
    "Share your favorite movie quote and explain why you love it"
]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'database': 'supabase'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.get_by_username(username)
        if existing_user:
            flash('Username already exists!')
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        user = User.create(username, password_hash)
        
        if user:
            login_user(user)
            flash('Registration successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Registration failed!')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's active games
    try:
        response = supabase.table('players').select('*, games(*)').eq('user_id', current_user.id).execute()
        user_games = response.data
    except Exception as e:
        print(f"Error getting user games: {e}")
        user_games = []
    
    return render_template('dashboard.html', user_games=user_games)

@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        name = request.form['name']
        admin_password = request.form['admin_password']
        
        # Convert to integers if provided
        if time_limit:
            time_limit = int(time_limit)
        if target_challenges:
            target_challenges = int(target_challenges)
        if max_vetos and max_vetos != '':
            max_vetos = int(max_vetos)
        else:
            max_vetos = 3
        
        game = Game.create(name, admin_password, game_mode, time_limit, target_challenges, max_vetos)
        if game:
            # Add creator as player
            game.add_player(current_user.id)
            flash(f'Game created! Code: {game.code}')
            return redirect(url_for('game_room', game_id=game.id))
        else:
            flash('Failed to create game!')
    
    return render_template('create_game.html')

@app.route('/join_game', methods=['GET', 'POST'])
@login_required
def join_game():
    if request.method == 'POST':
        code = request.form['code']
        
        game = Game.get_by_code(code)
        if game:
            # Check if user is already in the game
            players = game.get_players()
            if any(player['user_id'] == current_user.id for player in players):
                flash('You are already in this game!')
            else:
                game.add_player(current_user.id)
                flash('Successfully joined the game!')
                return redirect(url_for('game_room', game_id=game.id))
        else:
            flash('Invalid game code!')
    
    return render_template('join_game.html')

@app.route('/game/<int:game_id>')
@login_required
def game_room(game_id):
    game = Game.get(game_id)
    if not game:
        flash('Game not found!')
        return redirect(url_for('dashboard'))
    
    # Check if user is in the game
    players = game.get_players()
    if not any(player['user_id'] == current_user.id for player in players):
        flash('You are not in this game!')
        return redirect(url_for('dashboard'))
    
    # Check if user is admin (by checking admin password)
    is_admin = request.args.get('admin_password') == game.admin_password
    
    return render_template('game_room.html', game=game, players=players, is_admin=is_admin)

@app.route('/api/get_challenge/<int:game_id>')
@login_required
def get_challenge(game_id):
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Check if user is in the game
    players = game.get_players()
    if not any(player['user_id'] == current_user.id for player in players):
        return jsonify({'error': 'Not in game'}), 403
    
    # Get user's completed challenges
    completed_challenges = game.get_completed_challenges(current_user.id)
    completed_challenge_ids = [cc['challenge_id'] for cc in completed_challenges]
    
    # Get user's vetoes
    vetoes = game.get_vetoes(current_user.id)
    vetoed_challenge_ids = [v['challenge_id'] for v in vetoes]
    
    # Get all challenges
    try:
        response = supabase.table('challenges').select('*').execute()
        all_challenges = response.data
    except Exception as e:
        print(f"Error getting challenges: {e}")
        all_challenges = []
    
    # Filter out completed and vetoed challenges
    available_challenges = [
        c for c in all_challenges 
        if c['id'] not in completed_challenge_ids and c['id'] not in vetoed_challenge_ids
    ]
    
    if not available_challenges:
        return jsonify({'error': 'No more challenges available'}), 404
    
    # Select random challenge
    challenge = random.choice(available_challenges)
    
    # Get progress info
    total_challenges = len(all_challenges)
    completed_count = len(completed_challenges)
    vetoed_count = len(vetoes)
    
    return jsonify({
        'challenge': challenge,
        'progress': {
            'completed': completed_count,
            'vetoed': vetoed_count,
            'total': total_challenges,
            'remaining': total_challenges - completed_count - vetoed_count
        },
        'game_mode': game.game_mode,
        'target_challenges': game.target_challenges
    })

@app.route('/api/complete_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def complete_challenge(challenge_id):
    game_id = request.json.get('game_id')
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Complete the challenge
    result = game.complete_challenge(current_user.id, challenge_id)
    if not result:
        return jsonify({'error': 'Failed to complete challenge'}), 500
    
    # Check if game should end (winner takes all mode)
    if game.game_mode == 'winner_takes_all' and game.target_challenges:
        completed_challenges = game.get_completed_challenges(current_user.id)
        if len(completed_challenges) >= game.target_challenges:
            game.end_game(current_user.id)
            return jsonify({
                'message': 'Challenge completed! You won the game!',
                'game_ended': True,
                'winner': current_user.username
            })
    
    return jsonify({'message': 'Challenge completed!'})

@app.route('/api/veto_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def veto_challenge(challenge_id):
    game_id = request.json.get('game_id')
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Veto the challenge
    result = game.veto_challenge(current_user.id, challenge_id)
    if not result:
        return jsonify({'error': 'Failed to veto challenge'}), 500
    
    return jsonify({'message': 'Challenge vetoed!'})

@app.route('/api/end_game/<int:game_id>', methods=['POST'])
@login_required
def end_game(game_id):
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Check if user is admin
    is_admin = request.json.get('admin_password') == game.admin_password
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    # End the game
    result = game.end_game()
    if not result:
        return jsonify({'error': 'Failed to end game'}), 500
    
    return jsonify({'message': 'Game ended!'})

@app.route('/admin_login', methods=['POST'])
def admin_login():
    password = request.form['admin_password']
    if password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        flash('Admin login successful!')
        return redirect(url_for('admin_menu'))
    else:
        flash('Invalid admin password!')
        return redirect(url_for('index'))

@app.route('/admin_menu')
def admin_menu():
    if not session.get('admin_logged_in'):
        flash('Admin access required!')
        return redirect(url_for('index'))
    
    # Get all active games
    try:
        response = supabase.table('games').select('*').eq('is_active', True).execute()
        active_games = response.data
    except Exception as e:
        print(f"Error getting active games: {e}")
        active_games = []
    
    return render_template('admin_menu.html', games=active_games)

@app.route('/admin_create_game', methods=['GET', 'POST'])
def admin_create_game():
    if not session.get('admin_logged_in'):
        flash('Admin access required!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['game_name']
        max_vetos = request.form.get('max_vetos', 3)
        admin_password = request.form['admin_password'] if 'admin_password' in request.form else ADMIN_PASSWORD
        game_mode = request.form.get('game_mode', 'open_ended')
        time_limit = request.form.get('time_limit')
        target_challenges = request.form.get('target_challenges')
        
        # Convert to integers if provided
        if time_limit:
            time_limit = int(time_limit)
        if target_challenges:
            target_challenges = int(target_challenges)
        if max_vetos and max_vetos != '':
            max_vetos = int(max_vetos)
        
        game = Game.create(name, admin_password, game_mode, time_limit, target_challenges, max_vetos)
        if game:
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            join_url = request.host_url.rstrip('/') + url_for('join_game') + '?code=' + game.code
            qr.add_data(join_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            flash(f'Game created! Code: {game.code}')
            return render_template('admin_game_created.html', game=game, qr_code=img_str, join_url=join_url)
        else:
            flash('Failed to create game!')
    
    return render_template('admin_create_game.html')

@app.route('/admin_join_game/<int:game_id>')
def admin_join_game(game_id):
    if not session.get('admin_logged_in'):
        flash('Admin access required!')
        return redirect(url_for('index'))
    
    game = Game.get(game_id)
    if not game:
        flash('Game not found!')
        return redirect(url_for('admin_menu'))
    
    # Redirect to game room with admin access
    return redirect(url_for('game_room', game_id=game_id, admin_password=game.admin_password))

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Admin logged out!')
    return redirect(url_for('index'))

@app.route('/admin_change_password', methods=['GET', 'POST'])
def admin_change_password():
    if not session.get('admin_logged_in'):
        flash('Admin access required!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password == confirm_password:
            global ADMIN_PASSWORD
            ADMIN_PASSWORD = new_password
            flash('Admin password changed successfully!')
            return redirect(url_for('admin_menu'))
        else:
            flash('Passwords do not match!')
    
    return render_template('admin_change_password.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        # Initialize sample challenges if they don't exist
        try:
            response = supabase.table('challenges').select('*').limit(1).execute()
            if not response.data:
                print("Adding sample challenges...")
                for challenge_text in SAMPLE_CHALLENGES:
                    supabase.table('challenges').insert({'description': challenge_text}).execute()
                print("Sample challenges added!")
        except Exception as e:
            print(f"Error initializing challenges: {e}")
    
    app.run(debug=True) 