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
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'your-supabase-url-here')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', 'your-anon-key-here')

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
                    is_admin=False,  # Default to False since we don't store this in DB
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
                    is_admin=False,  # Default to False since we don't store this in DB
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
                'password_hash': password_hash
            }).execute()
            if response.data:
                user_data = response.data[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    is_admin=False,  # Default to False since we don't store this in DB
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

    def get_failed_challenges(self, user_id):
        """Get failed challenges for a user in this game"""
        try:
            response = supabase.table('failed_challenges').select('*').eq('game_id', self.id).eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting failed challenges: {e}")
            return []

    def get_used_challenges_in_game(self):
        """Get all challenges that have been used in this game (by any player)"""
        try:
            used_challenges = set()
            
            # Get completed challenges
            response = supabase.table('completed_challenges').select('challenge_id').eq('game_id', self.id).execute()
            if response.data:
                used_challenges.update([cc['challenge_id'] for cc in response.data])
            
            # Get vetoed challenges
            response = supabase.table('vetoes').select('challenge_id').eq('game_id', self.id).execute()
            if response.data:
                used_challenges.update([v['challenge_id'] for v in response.data])
            
            # Get failed challenges
            response = supabase.table('failed_challenges').select('challenge_id').eq('game_id', self.id).execute()
            if response.data:
                used_challenges.update([fc['challenge_id'] for fc in response.data])
            
            return used_challenges
        except Exception as e:
            print(f"Error getting used challenges in game: {e}")
            return set()

    def get_available_challenges_for_user(self, user_id):
        """Get challenges available for a specific user in this game"""
        try:
            # Get all challenges
            response = supabase.table('challenges').select('*').execute()
            all_challenges = response.data
            
            # Get challenges used by this specific user
            user_completed = set([cc['challenge_id'] for cc in self.get_completed_challenges(user_id)])
            user_vetoed = set([v['challenge_id'] for v in self.get_vetoes(user_id)])
            user_failed = set([fc['challenge_id'] for fc in self.get_failed_challenges(user_id)])
            
            # Get challenges used by ANY player in this game
            game_used = self.get_used_challenges_in_game()
            
            # Filter out challenges that are unavailable
            available_challenges = [
                c for c in all_challenges 
                if c['id'] not in user_completed and 
                   c['id'] not in user_vetoed and 
                   c['id'] not in user_failed and
                   c['id'] not in game_used  # This ensures no duplicates within the game session
            ]
            
            return available_challenges
        except Exception as e:
            print(f"Error getting available challenges for user: {e}")
            return []

    def fail_challenge(self, user_id, challenge_id):
        """Mark a challenge as failed"""
        try:
            response = supabase.table('failed_challenges').insert({
                'game_id': self.id,
                'user_id': user_id,
                'challenge_id': challenge_id
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error failing challenge: {e}")
            return None

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
        """End the game and set winner"""
        try:
            response = supabase.table('games').update({
                'is_active': False,
                'winner_id': winner_id
            }).eq('id', self.id).execute()
            return response.data
        except Exception as e:
            print(f"Error ending game: {e}")
            return None

    @staticmethod
    def clear_all_users():
        """Clear all users from the database (for fresh game sessions)"""
        try:
            # Delete all users except admin users (those starting with 'admin_')
            response = supabase.table('users').delete().neq('username', 'admin').execute()
            print(f"Cleared {len(response.data) if response.data else 0} users from database")
            return True
        except Exception as e:
            print(f"Error clearing users: {e}")
            return False

    @staticmethod
    def cleanup_old_users(hours_old=24):
        """Clean up users who haven't been active for the specified number of hours"""
        try:
            # Calculate the cutoff time
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours_old)
            
            # Get users created before the cutoff time (excluding admin users)
            response = supabase.table('users').select('id, username, created_at').lt('created_at', cutoff_time.isoformat()).neq('username', 'admin').execute()
            
            if response.data:
                user_ids = [user['id'] for user in response.data]
                
                # Delete related data first
                for user_id in user_ids:
                    # Delete completed challenges
                    supabase.table('completed_challenges').delete().eq('user_id', user_id).execute()
                    # Delete vetoes
                    supabase.table('vetoes').delete().eq('user_id', user_id).execute()
                    # Delete failed challenges
                    supabase.table('failed_challenges').delete().eq('user_id', user_id).execute()
                    # Delete player entries
                    supabase.table('players').delete().eq('user_id', user_id).execute()
                
                # Delete the users
                supabase.table('users').delete().in_('id', user_ids).execute()
                
                print(f"Cleaned up {len(user_ids)} old users (older than {hours_old} hours)")
                return len(user_ids)
            else:
                print("No old users to clean up")
                return 0
                
        except Exception as e:
            print(f"Error cleaning up old users: {e}")
            return 0

    @staticmethod
    def clear_game_data(game_id):
        """Clear all data related to a specific game"""
        try:
            # Delete completed challenges for this game
            supabase.table('completed_challenges').delete().eq('game_id', game_id).execute()
            # Delete vetoes for this game
            supabase.table('vetoes').delete().eq('game_id', game_id).execute()
            # Delete failed challenges for this game
            supabase.table('failed_challenges').delete().eq('game_id', game_id).execute()
            # Delete players for this game
            supabase.table('players').delete().eq('game_id', game_id).execute()
            print(f"Cleared all data for game {game_id}")
            return True
        except Exception as e:
            print(f"Error clearing game data: {e}")
            return False

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

# Sample challenges for initialization - Updated with new missions!
SAMPLE_CHALLENGES = [
    "Get someone to say the word \"penguin\" in conversation",
    "Make someone high-five you twice in under a minute",
    "Get someone to give you a snack without asking for one",
    "Make someone take a selfie with you",
    "Convince someone to sing a line from any song out loud",
    "Get someone to compliment your shoes",
    "Get someone to guess a number between 1 and 10",
    "Convince someone to make an animal noise",
    "Get someone to smell something you're holding",
    "Make someone tell you a childhood nickname",
    "Convince someone to put on a hat or something hat-like",
    "Get someone to throw an item at you",
    "Get someone to use a fake accent when talking to you",
    "Convince someone to spell a word out loud",
    "Get someone to clink glasses with you twice in five minutes",
    "Make someone use their phone's flashlight for you",
    "Get someone to teach you a dance move",
    "Convince someone to tell you a fun fact they \"just remembered\"",
    "Convince someone to apologise to you for something they didn't do",
    "Get someone to give you something blue",
    "Make someone \"cheers\" you without you holding a drink",
    "Convince someone to say \"that's a great idea\"",
    "Get someone to teach you a life hack",
    "Make someone draw you a picture",
    "Convince someone to lend you their phone for a photo, then take a selfie with it",
    "Make someone swap an item of clothing with you",
    "Convince someone to close their eyes for at least five seconds",
    "Get someone to tell you what's in their pocket or bag",
    "Get someone to whisper something to you",
    "Make someone give you a round of applause",
    "Get someone to say the word \"banana\"",
    "Convince someone to hum a tune with you",
    "Make someone tell you the time without checking their phone or watch",
    "Get someone to compliment your hair",
    "Convince someone to tell you a joke",
    "Get someone to dance for at least five seconds",
    "Convince someone to tell you a movie they've watched more than once",
    "Get someone to make a heart shape with their hands",
    "Get someone to Google something for you",
    "Make someone say \"cheers\" in another language",
    "Convince someone to whistle",
    "Get someone to name a country starting with M",
    "Make someone tell you their favourite pizza topping",
    "Get someone to take a bite of something you're holding",
    "Convince someone to hand you their drink",
    "Get someone to imitate a celebrity",
    "Convince someone to give you a nickname",
    "Make someone write something down for you",
    "Convince someone to stand in a spot \"for a photo\" and don't take one",
    "Get someone to guess your star sign",
    "Convince someone to show you a picture on their phone",
    "Get someone to quote a movie",
    "Make someone switch seats with you",
    "Convince someone to clap for you",
    "Convince someone to tell you their most-used emoji",
    "Get someone to say \"I give up\"",
    "Convince someone to draw a picture of you",
    "Make someone tell you their middle name",
    "Get someone to show you the inside of their shoes",
    "Convince someone to say \"deal\" to you",
    "Get someone to wear something on their head that isn't a hat",
    "Make someone tell you a secret (real or fake)",
    "Convince someone to stand back-to-back with you",
    "Convince someone to lend you their phone and take a silly selfie with it",
    "Get someone to call you the wrong name for at least five minutes",
    "Convince someone to help you find something that doesn't exist",
    "Get someone to hold something for you for more than two minutes",
    "Make someone say \"this is ridiculous\"",
    "Get someone to tell you their earliest memory",
    "Convince someone to balance something on their head",
    "Get someone to agree the moon is overrated",
    "Convince someone to toast \"to chaos\" with you",
    "Get someone to tell you their biggest irrational fear",
    "Get someone to compliment something that doesn't exist",
    "Convince someone to help you measure something with their arms",
    "Get someone to compare you to a food item",
    "Get someone to invent a handshake with you",
    "Convince someone to count down from ten",
    "Get someone to try guessing your password (don't tell them)",
    "Get someone to say the word \"pickle\"",
    "Convince someone to sing a national anthem",
    "Get something from someone's hair",
    "Convince someone to argue about whether cereal is soup",
    "Get someone to agree that the floor is lava for at least ten seconds",
    "Get someone to say the word \"moist\"",
    "Convince someone to tell you their \"villain origin story\"",
    "Get someone to explain why they'd survive a zombie apocalypse",
    "Convince someone to decide on a mascot for the party",
    "Convince someone to rank at least five fruits from best to worst",
    "Get someone to give a toast to something absurd (e.g., \"to spoons!\")",
    "Convince someone to pick a celebrity to be your body double",
    "Convince someone to teach you how to wink \"properly\"",
    "Convince someone to try to guess the exact number of steps they've taken today",
    "Get someone to agree to start a fake club with you",
    "Convince someone to tell you what your \"aura colour\" is",
    "Get someone to choose which dinosaur you would be and why",
    "Convince someone to agree to a handshake but then turn it into a secret ritual",
    "Get someone to \"rate\" your smile on a scale of 1 to 17",
    "Get someone to tell you which historical figure you remind them of",
    "Convince someone to list the pros and cons of potatoes",
    "Convince someone to choose a theme song for your life",
    "Get someone to come up with a catchphrase for you",
    "Convince someone to guess your \"superpower\" and how you use it",
    "Convince someone to pick a made-up title for you (\"Supreme Ruler of…\")",
    "Get someone to tell you what planet you'd be from if you were an alien",
    "Get someone to tell you which animal would make the worst pet",
    "Tell someone you're worried you've accidentally joined a cult",
    "Casually mention that you think your neighbour might be a spy",
    "Tell someone you've been banned from using microwaves (don't explain why unless asked)",
    "Confess that you think you might be allergic to moonlight",
    "Say you're considering changing your name to something completely unpronounceable",
    "Tell someone you're training for a world record, but don't say which one until they ask",
    "Casually mention that you've been followed by the same pigeon for three days",
    "Tell someone you think your phone is haunted",
    "Casually drop into conversation that you've started writing a self-help book",
    "Mention that you think one of the guests is an undercover celebrity",
    "Confess that you've been banned from three group chats this week",
    "Casually mention that you once spent an entire day without speaking to see if anyone noticed",
    "Tell someone you've been trying to learn a new skill but you're too embarrassed to say what it is",
    "Say you have a strange superstition you follow every Friday",
    "Tell someone you once had an odd job for just one day before quitting",
    "Casually mention that you've been eating the same lunch for months and you're starting to worry about it",
    "Tell someone you think you might have a very niche talent",
    "Tell someone you recently realised you've been pronouncing a common word wrong your whole life",
    "Casually mention that you always carry something unusual in your bag or pocket",
    "Tell someone you have a favourite seat in every room of your house",
    "Casually mention that you've been mistaken for someone else multiple times this month",
    "Tell someone you have a strange party habit that no one's noticed yet",
    "Tell someone you once learned something years too late that everyone else seemed to already know",
]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'database': 'supabase'})

@app.route('/status')
def status():
    return jsonify({
        'message': 'Covert Agenda is running!',
        'status': 'success',
        'version': '1.0.0',
        'app': 'app_supabase.py',
        'branch': 'simple-version'
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Prevent users from registering with admin-like usernames
        if username.startswith('admin_'):
            flash('Username cannot start with "admin_"!')
            return render_template('register.html')
        
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

@app.route('/join_game_anonymous', methods=['GET', 'POST'])
def join_game_anonymous():
    """Allow users to join games without requiring login by creating a temporary account"""
    if request.method == 'POST':
        code = request.form['code']
        username = request.form['username']
        
        # Validate username
        if not username or len(username.strip()) < 2:
            flash('Username must be at least 2 characters long!')
            return render_template('join_game_anonymous.html', game_code=code)
        
        username = username.strip()
        
        # Check if username starts with admin_ (reserved for admin users)
        if username.startswith('admin_'):
            flash('Username cannot start with "admin_"!')
            return render_template('join_game_anonymous.html', game_code=code)
        
        game = Game.get_by_code(code)
        if not game:
            flash('Invalid game code!')
            return render_template('join_game_anonymous.html')
        
        # Check if username already exists
        existing_user = User.get_by_username(username)
        if existing_user:
            flash('Username already exists! Please choose a different one.')
            return render_template('join_game_anonymous.html', game_code=code)
        
        # Create new user with a simple password (they won't need to log in again)
        password_hash = generate_password_hash('temp123')
        user = User.create(username, password_hash)
        
        if not user:
            flash('Failed to create user account!')
            return render_template('join_game_anonymous.html', game_code=code)
        
        # Log the user in
        login_user(user)
        
        # Add user to the game
        game.add_player(user.id)
        flash('Successfully joined the game!')
        return redirect(url_for('game_room', game_id=game.id))
    
    # Handle GET request with game code parameter
    game_code = request.args.get('code', '').strip()
    return render_template('join_game_anonymous.html', game_code=game_code)

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
    
    # Check if game has ended - redirect to end game screen
    if not game.is_active:
        return redirect(url_for('end_game_screen', game_id=game_id))
    
    # Check if user is admin (by checking admin password, admin session, or admin username pattern)
    is_admin = (request.args.get('admin_password') == game.admin_password or 
                session.get('admin_logged_in') or
                current_user.username.startswith('admin_'))
    
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
    
    # Get available challenges for this user (no duplicates within game session)
    available_challenges = game.get_available_challenges_for_user(current_user.id)
    
    if not available_challenges:
        return jsonify({'error': 'No more challenges available'}), 404
    
    # Use improved randomization: shuffle and pick first, or weighted selection
    # This provides better distribution than simple random.choice
    random.shuffle(available_challenges)
    challenge = available_challenges[0]
    
    # Get user's progress for display
    completed_challenges = game.get_completed_challenges(current_user.id)
    vetoes = game.get_vetoes(current_user.id)
    failed_challenges = game.get_failed_challenges(current_user.id)
    
    # Get progress info
    try:
        response = supabase.table('challenges').select('*').execute()
        total_challenges = len(response.data)
    except Exception as e:
        print(f"Error getting total challenges: {e}")
        total_challenges = 0
    
    completed_count = len(completed_challenges)
    vetoed_count = len(vetoes)
    failed_count = len(failed_challenges)
    
    return jsonify({
        'challenge': challenge,
        'progress': {
            'completed': completed_count,
            'vetoed': vetoed_count,
            'failed': failed_count,
            'total': total_challenges,
            'remaining': total_challenges - completed_count - vetoed_count - failed_count
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

@app.route('/api/fail_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def fail_challenge(challenge_id):
    game_id = request.json.get('game_id')
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Fail the challenge
    result = game.fail_challenge(current_user.id, challenge_id)
    if not result:
        return jsonify({'error': 'Failed to mark challenge as failed'}), 500
    
    return jsonify({'message': 'Challenge marked as failed!'})

@app.route('/api/get_players/<int:game_id>')
@login_required
def get_players(game_id):
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Check if user is in the game
    players = game.get_players()
    if not any(player['user_id'] == current_user.id for player in players):
        return jsonify({'error': 'Not in game'}), 403
    
    # Format players data for frontend
    formatted_players = []
    for player in players:
        formatted_players.append({
            'id': player['user_id'],
            'username': player['users']['username'] if player['users'] else f'Player {player["user_id"]}',
            'is_admin': (player['users']['username'].startswith('admin_') or player['users']['username'].startswith('Admin')) if player['users'] and player['users']['username'] else False,
            'joined_at': player['joined_at']
        })
    
    return jsonify({'players': formatted_players})

@app.route('/api/game_status/<int:game_id>')
@login_required
def game_status(game_id):
    """Check if a game is still active"""
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    return jsonify({
        'is_active': game.is_active,
        'game_id': game_id
    })

@app.route('/admin_api/get_players/<int:game_id>')
def admin_get_players(game_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin access required'}), 403
    
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Format players data for frontend
    formatted_players = []
    for player in game.get_players():
        formatted_players.append({
            'id': player['user_id'],
            'username': player['users']['username'] if player['users'] else f'Player {player["user_id"]}',
            'is_admin': (player['users']['username'].startswith('admin_') or player['users']['username'].startswith('Admin')) if player['users'] and player['users']['username'] else False,
            'joined_at': player['joined_at']
        })
    
    return jsonify({'players': formatted_players})

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
    
    # Get all players in the game
    players = game.get_players()
    
    # Calculate scores for each player
    player_stats = []
    best_score = -1
    
    for player_data in players:
        user_id = player_data['user_id']
        username = player_data['users']['username']
        
        # Get completed challenges
        completed_challenges = game.get_completed_challenges(user_id)
        completed_count = len(completed_challenges)
        
        # Get failed challenges
        failed_challenges = game.get_failed_challenges(user_id)
        failed_count = len(failed_challenges)
        
        # Get vetoed challenges
        vetoes = game.get_vetoes(user_id)
        vetoed_count = len(vetoes)
        
        # Calculate score: completed - failed (negative points for failures)
        score = completed_count - failed_count
        
        player_stats.append({
            'username': username,
            'completed': completed_count,
            'failed': failed_count,
            'vetoed': vetoed_count,
            'score': score
        })
        
        # Track best score
        if score > best_score:
            best_score = score
    
    # Determine winner(s) with tie-breaking
    winners = []
    for player in player_stats:
        if player['score'] == best_score:
            winners.append(player)
    
    # If there's a tie, apply tie-breaking rules
    if len(winners) > 1:
        # Sort by tie-breaking criteria: completed desc, failed asc, vetoed asc
        winners.sort(key=lambda x: (-x['completed'], x['failed'], x['vetoed']))
        
        # Check if still tied after tie-breaking
        if (winners[0]['completed'] == winners[1]['completed'] and 
            winners[0]['failed'] == winners[1]['failed'] and 
            winners[0]['vetoed'] == winners[1]['vetoed']):
            # True tie - multiple winners
            winner = "TIE"
            winner_names = [w['username'] for w in winners]
        else:
            # Tie broken
            winner = winners[0]['username']
            winner_names = [winner]
    else:
        # Single winner
        winner = winners[0]['username']
        winner_names = [winner]

    # End the game
    result = game.end_game()
    if not result:
        return jsonify({'error': 'Failed to end game'}), 500
    
    return jsonify({
        'message': f'Game ended! Winner: {winner} with score {best_score}',
        'winner': winner,
        'best_score': best_score,
        'player_stats': player_stats,
        'redirect': url_for('end_game_screen', game_id=game_id)
    })

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
        admin_username = request.form.get('admin_username', 'Admin')
        max_vetos = request.form.get('max_vetos', 3)
        admin_password = request.form['admin_password'] if 'admin_password' in request.form else ADMIN_PASSWORD
        game_mode = request.form.get('game_mode', 'open_ended')
        time_limit = request.form.get('time_limit')
        target_challenges = request.form.get('target_challenges')
        clear_users = 'clear_users' in request.form  # Check if user wants to clear all users
        
        # Store admin username in session for later use
        session['admin_username'] = admin_username
        
        # Convert to integers if provided
        if time_limit:
            time_limit = int(time_limit)
        if target_challenges:
            target_challenges = int(target_challenges)
        if max_vetos and max_vetos != '':
            max_vetos = int(max_vetos)
        
        # Clear all users if requested (for fresh game sessions)
        if clear_users:
            Game.clear_all_users()
            flash('All users cleared for fresh game session!')
        else:
            # Automatically clean up old users (older than 24 hours)
            cleaned_count = Game.cleanup_old_users(hours_old=24)
            if cleaned_count > 0:
                flash(f'Automatically cleaned up {cleaned_count} old users (older than 24 hours)')
        
        game = Game.create(name, admin_password, game_mode, time_limit, target_challenges, max_vetos)
        if game:
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            join_url = request.host_url.rstrip('/') + url_for('join_game_anonymous') + '?code=' + game.code
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

@app.route('/admin_clear_users', methods=['POST'])
def admin_clear_users():
    """Admin route to clear all users from the database"""
    if not session.get('admin_logged_in'):
        flash('Admin access required!')
        return redirect(url_for('index'))
    
    if Game.clear_all_users():
        flash('All users cleared successfully! Usernames can now be reused.')
    else:
        flash('Failed to clear users!')
    
    return redirect(url_for('admin_menu'))

@app.route('/admin_join_game/<int:game_id>')
def admin_join_game(game_id):
    if not session.get('admin_logged_in'):
        flash('Admin access required!')
        return redirect(url_for('index'))
    
    game = Game.get(game_id)
    if not game:
        flash('Game not found!')
        return redirect(url_for('admin_menu'))
    
    # Get admin username from session or use default
    admin_username = session.get('admin_username', f'Admin_{game_id}')
    
    # Create admin user with the custom username
    admin_user = User.get_by_username(admin_username)
    if not admin_user:
        password_hash = generate_password_hash('admin')
        admin_user = User.create(admin_username, password_hash)
        if not admin_user:
            flash('Failed to create admin user!')
            return redirect(url_for('admin_menu'))
    
    # Add admin to the game if not already there
    players = game.get_players()
    if not any(player['user_id'] == admin_user.id for player in players):
        game.add_player(admin_user.id)
        flash('Admin joined the game as a player!')
    
    # Log in as admin user
    login_user(admin_user)
    
    # Redirect to regular game room (now admin can play with others)
    return redirect(url_for('game_room', game_id=game_id))

@app.route('/admin_game_room/<int:game_id>')
def admin_game_room(game_id):
    if not session.get('admin_logged_in'):
        flash('Admin access required!')
        return redirect(url_for('index'))
    
    game = Game.get(game_id)
    if not game:
        flash('Game not found!')
        return redirect(url_for('admin_menu'))
    
    # Get players in the game
    players = game.get_players()
    
    # Admin has full access in admin game room
    is_admin = True
    
    return render_template('game_room.html', game=game, players=players, is_admin=is_admin)

@app.route('/admin_api/get_challenge/<int:game_id>')
def admin_get_challenge(game_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin access required'}), 403
    
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Get all challenges
    try:
        response = supabase.table('challenges').select('*').execute()
        all_challenges = response.data
    except Exception as e:
        print(f"Error getting challenges: {e}")
        all_challenges = []
    
    if not all_challenges:
        return jsonify({'error': 'No challenges available'}), 404
    
    # For admin, we can show any challenge, but let's still use improved randomization
    # and avoid challenges that have been used in this game session
    game_used = game.get_used_challenges_in_game()
    available_challenges = [c for c in all_challenges if c['id'] not in game_used]
    
    # If all challenges have been used, fall back to all challenges
    if not available_challenges:
        available_challenges = all_challenges
    
    # Use improved randomization
    random.shuffle(available_challenges)
    challenge = available_challenges[0]
    
    return jsonify({
        'challenge': challenge,
        'progress': {
            'completed': 0,
            'vetoed': 0,
            'total': len(all_challenges),
            'remaining': len(all_challenges)
        },
        'game_mode': game.game_mode,
        'target_challenges': game.target_challenges
    })

@app.route('/admin_api/complete_challenge/<int:challenge_id>', methods=['POST'])
def admin_complete_challenge(challenge_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin access required'}), 403
    
    game_id = request.json.get('game_id')
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # For admin, just return success (no actual completion tracking)
    return jsonify({'message': 'Challenge completed! (Admin mode)'})

@app.route('/admin_api/veto_challenge/<int:challenge_id>', methods=['POST'])
def admin_veto_challenge(challenge_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin access required'}), 403
    
    game_id = request.json.get('game_id')
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # For admin, just return success (no actual veto tracking)
    return jsonify({'message': 'Challenge vetoed! (Admin mode)'})

@app.route('/end_game_screen/<int:game_id>')
def end_game_screen(game_id):
    """Display the end game screen with final scores and winner"""
    game = Game.get(game_id)
    if not game:
        flash('Game not found!')
        return redirect(url_for('index'))
    
    # Check if game is actually ended
    if game.is_active:
        flash('Game is still active!')
        return redirect(url_for('game_room', game_id=game_id))
    
    # Get all players in the game
    players = game.get_players()
    
    # Calculate scores for each player
    player_stats = []
    best_score = -1
    
    for player_data in players:
        user_id = player_data['user_id']
        username = player_data['users']['username']
        
        # Get completed challenges
        completed_challenges = game.get_completed_challenges(user_id)
        completed_count = len(completed_challenges)
        
        # Get failed challenges
        failed_challenges = game.get_failed_challenges(user_id)
        failed_count = len(failed_challenges)
        
        # Get vetoed challenges
        vetoes = game.get_vetoes(user_id)
        vetoed_count = len(vetoes)
        
        # Calculate score: completed - failed (negative points for failures)
        score = completed_count - failed_count
        
        player_stats.append({
            'username': username,
            'completed': completed_count,
            'failed': failed_count,
            'vetoed': vetoed_count,
            'score': score
        })
        
        # Track winner (highest score)
        if score > best_score:
            best_score = score
    
    # Determine winner(s) with tie-breaking
    winners = []
    for player in player_stats:
        if player['score'] == best_score:
            winners.append(player)
    
    # If there's a tie, apply tie-breaking rules
    if len(winners) > 1:
        # Sort by tie-breaking criteria: completed desc, failed asc, vetoed asc
        winners.sort(key=lambda x: (-x['completed'], x['failed'], x['vetoed']))
        
        # Check if still tied after tie-breaking
        if (winners[0]['completed'] == winners[1]['completed'] and 
            winners[0]['failed'] == winners[1]['failed'] and 
            winners[0]['vetoed'] == winners[1]['vetoed']):
            # True tie - multiple winners
            winner = "TIE"
            winner_names = [w['username'] for w in winners]
        else:
            # Tie broken
            winner = winners[0]['username']
            winner_names = [winner]
    else:
        # Single winner
        winner = winners[0]['username']
        winner_names = [winner]
    
    # Calculate ranks with proper tie handling
    ranked_players = []
    current_rank = 1
    current_score = -1
    current_completed = -1
    current_failed = -1
    current_vetoed = -1
    
    for i, player in enumerate(sorted(player_stats, key=lambda x: (-x['score'], -x['completed'], x['failed'], x['vetoed']))):
        # Check if this is a tie with the previous player
        is_tie = (player['score'] == current_score and 
                  player['completed'] == current_completed and 
                  player['failed'] == current_failed and 
                  player['vetoed'] == current_vetoed)
        
        if not is_tie:
            current_rank = i + 1
        
        # Add rank to player data
        player_with_rank = player.copy()
        player_with_rank['rank'] = current_rank
        ranked_players.append(player_with_rank)
        
        # Update current values for next iteration
        current_score = player['score']
        current_completed = player['completed']
        current_failed = player['failed']
        current_vetoed = player['vetoed']

    return render_template('end_game.html', 
                         game=game, 
                         player_stats=ranked_players, 
                         winner=winner, 
                         winner_names=winner_names, 
                         best_score=best_score)

@app.route('/admin_api/end_game/<int:game_id>', methods=['POST'])
def admin_end_game(game_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Admin access required'}), 403
    
    game = Game.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # End the game
    result = game.end_game()
    if not result:
        return jsonify({'error': 'Failed to end game'}), 500
    
    return jsonify({'message': 'Game ended!', 'redirect': url_for('end_game_screen', game_id=game_id)})

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
    
    app.run(debug=True, port=4000) 