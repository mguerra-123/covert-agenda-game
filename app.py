from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
import uuid
import os
from datetime import datetime, timedelta
import qrcode
import io
import base64
from dotenv import set_key, load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///game.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Fix for Render PostgreSQL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Admin password - you can change this
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_finished = db.Column(db.Boolean, default=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    max_vetos = db.Column(db.Integer, default=3)  # New field for customizable vetos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GamePlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')
    category = db.Column(db.String(50), default='general')

class PlayerChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_vetoed = db.Column(db.Boolean, default=False)
    is_failed = db.Column(db.Boolean, default=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Sample challenges
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

def generate_game_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

def get_random_challenge():
    return random.choice(SAMPLE_CHALLENGES)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({'status': 'healthy', 'message': 'Challenge Game is running!'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        # Basic validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_games = Game.query.filter_by(admin_id=current_user.id).all()
    joined_games = Game.query.join(GamePlayer).filter(GamePlayer.user_id == current_user.id).all()
    
    # If user is admin, also show all admin-created games
    admin_games = []
    if current_user.is_admin:
        admin_games = Game.query.filter_by(admin_id=current_user.id).all()
    
    return render_template('dashboard.html', 
                         user_games=user_games, 
                         joined_games=joined_games, 
                         admin_games=admin_games,
                         is_admin=current_user.is_admin)

@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        game_name = request.form['game_name'].strip()
        
        if len(game_name) < 3:
            flash('Game name must be at least 3 characters long')
            return redirect(url_for('create_game'))
        
        game_code = generate_game_code()
        
        game = Game(name=game_name, code=game_code, admin_id=current_user.id)
        db.session.add(game)
        db.session.commit()
        
        flash(f'Game created! Code: {game_code}')
        return redirect(url_for('game_room', game_id=game.id))
    
    return render_template('create_game.html')

@app.route('/join_game', methods=['GET', 'POST'])
@login_required
def join_game():
    if request.method == 'POST':
        game_code = request.form['game_code'].upper().strip()
        
        if len(game_code) != 6:
            flash('Game code must be 6 characters long')
            return redirect(url_for('join_game'))
        
        game = Game.query.filter_by(code=game_code, is_active=True).first()
        
        if not game:
            flash('Invalid game code or game is not active')
            return redirect(url_for('join_game'))
        
        # Allow admin to join their own game as a player
        existing_player = GamePlayer.query.filter_by(game_id=game.id, user_id=current_user.id).first()
        if existing_player:
            flash('You are already in this game')
            return redirect(url_for('join_game'))
        
        player = GamePlayer(game_id=game.id, user_id=current_user.id)
        db.session.add(player)
        db.session.commit()
        
        flash('Successfully joined the game!')
        return redirect(url_for('game_room', game_id=game.id))
    
    # Handle QR code parameter
    game_code = request.args.get('code', '').upper().strip()
    return render_template('join_game.html', game_code=game_code)

@app.route('/game/<int:game_id>')
@login_required
def game_room(game_id):
    game = Game.query.get_or_404(game_id)
    players = User.query.join(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    is_player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first() is not None
    is_admin = game.admin_id == current_user.id
    
    # Allow access if user is either a player or the admin
    if not is_player and not is_admin:
        flash('You are not part of this game')
        return redirect(url_for('dashboard'))
    
    return render_template('game_room.html', game=game, players=players, is_admin=is_admin)

@app.route('/api/get_challenge/<int:game_id>')
@login_required
def get_challenge(game_id):
    game = Game.query.get_or_404(game_id)
    if not game.is_active:
        return jsonify({'error': 'Game is not active'})
    
    # Check if user is in the game (either as player or admin)
    player = GamePlayer.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    is_admin = game.admin_id == current_user.id
    
    if not player and not is_admin:
        return jsonify({'error': 'You are not in this game'})
    
    # Get current active challenge
    current_challenge = PlayerChallenge.query.filter_by(
        game_id=game_id, 
        user_id=current_user.id, 
        is_completed=False,
        is_vetoed=False,
        is_failed=False
    ).first()
    
    # Get completed count for winner takes all mode
    completed_count = PlayerChallenge.query.filter_by(
        game_id=game_id,
        user_id=current_user.id,
        is_completed=True
    ).count()
    
    if current_challenge:
        challenge = Challenge.query.get(current_challenge.challenge_id)
        return jsonify({
            'challenge_id': current_challenge.id,
            'description': challenge.description,
            'vetoes_used': PlayerChallenge.query.filter_by(
                game_id=game_id, 
                user_id=current_user.id, 
                is_vetoed=True
            ).count(),
            'max_vetos': game.max_vetos,
            'failed_count': PlayerChallenge.query.filter_by(
                game_id=game_id, 
                user_id=current_user.id, 
                is_failed=True
            ).count(),
            'completed_count': completed_count
        })
    
    # Assign new challenge
    challenge = Challenge(description=get_random_challenge())
    db.session.add(challenge)
    db.session.commit()
    
    player_challenge = PlayerChallenge(
        game_id=game_id,
        user_id=current_user.id,
        challenge_id=challenge.id
    )
    db.session.add(player_challenge)
    db.session.commit()
    
    # Get the actual veto count for this user in this game
    vetoes_used = PlayerChallenge.query.filter_by(
        game_id=game_id,
        user_id=current_user.id,
        is_vetoed=True
    ).count()
    
    # Get the failed count for this user in this game
    failed_count = PlayerChallenge.query.filter_by(
        game_id=game_id,
        user_id=current_user.id,
        is_failed=True
    ).count()
    
    return jsonify({
        'challenge_id': player_challenge.id,
        'description': challenge.description,
        'vetoes_used': vetoes_used,
        'max_vetos': game.max_vetos,
        'failed_count': failed_count,
        'completed_count': completed_count
    })

@app.route('/api/complete_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def complete_challenge(challenge_id):
    player_challenge = PlayerChallenge.query.get_or_404(challenge_id)
    
    if player_challenge.user_id != current_user.id:
        return jsonify({'error': 'Not your challenge'})
    
    player_challenge.is_completed = True
    player_challenge.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/veto_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def veto_challenge(challenge_id):
    player_challenge = PlayerChallenge.query.get_or_404(challenge_id)
    
    if player_challenge.user_id != current_user.id:
        return jsonify({'error': 'Not your challenge'})
    
    # Get game to check max_vetos setting
    game = Game.query.get(player_challenge.game_id)
    if not game:
        return jsonify({'error': 'Game not found'})
    
    # Check veto limit using game's max_vetos setting
    vetoes_used = PlayerChallenge.query.filter_by(
        game_id=player_challenge.game_id,
        user_id=current_user.id,
        is_vetoed=True
    ).count()
    
    if vetoes_used >= game.max_vetos:
        return jsonify({'error': f'You have used all your mission skips ({game.max_vetos})'})
    
    player_challenge.is_vetoed = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/fail_challenge/<int:challenge_id>', methods=['POST'])
@login_required
def fail_challenge(challenge_id):
    player_challenge = PlayerChallenge.query.get_or_404(challenge_id)
    
    if player_challenge.user_id != current_user.id:
        return jsonify({'error': 'Not your challenge'})
    
    player_challenge.is_failed = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/end_game/<int:game_id>', methods=['POST'])
@login_required
def end_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.admin_id != current_user.id:
        return jsonify({'error': 'Only admin can end the game'})
    
    # Calculate winner (player with most completed challenges)
    # Include both regular players and admin if they're also a player
    players = User.query.join(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    
    # Also include admin if they're not already in the players list
    admin_user = User.query.get(game.admin_id)
    if admin_user and admin_user not in players:
        players.append(admin_user)
    
    winner = None
    max_completed = 0
    player_stats = []
    
    for player in players:
        completed_count = PlayerChallenge.query.filter_by(
            game_id=game_id,
            user_id=player.id,
            is_completed=True
        ).count()
        
        failed_count = PlayerChallenge.query.filter_by(
            game_id=game_id,
            user_id=player.id,
            is_failed=True
        ).count()
        
        vetoed_count = PlayerChallenge.query.filter_by(
            game_id=game_id,
            user_id=player.id,
            is_vetoed=True
        ).count()
        
        player_stats.append({
            'username': player.username,
            'completed': completed_count,
            'failed': failed_count,
            'vetoed': vetoed_count
        })
        
        if completed_count > max_completed:
            max_completed = completed_count
            winner = player
    
    game.is_finished = True
    game.is_active = False
    if winner:
        game.winner_id = winner.id
    db.session.commit()
    
    return jsonify({
        'success': True,
        'winner': winner.username if winner else None,
        'completed_challenges': max_completed,
        'player_stats': player_stats
    })

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

@app.route('/admin_create_game', methods=['GET', 'POST'])
def admin_create_game():
    if not session.get('is_admin'):
        flash('Admin access required')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        game_name = request.form['game_name'].strip()
        max_vetos = int(request.form.get('max_vetos', 3))
        
        if len(game_name) < 3:
            flash('Game name must be at least 3 characters long')
            return redirect(url_for('admin_create_game'))
        
        if max_vetos < 0 or max_vetos > 10:
            flash('Max vetos must be between 0 and 10')
            return redirect(url_for('admin_create_game'))
        
        game_code = generate_game_code()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
        
        game = Game(
            name=game_name, 
            code=game_code, 
            admin_id=admin_user.id,
            max_vetos=max_vetos
        )
        db.session.add(game)
        db.session.commit()
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        join_url = request.host_url.rstrip('/') + url_for('join_game') + '?code=' + game_code
        qr.add_data(join_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        flash(f'Game created! Code: {game_code}')
        return render_template('admin_game_created.html', game=game, qr_code=img_str, join_url=join_url)
    
    return render_template('admin_create_game.html')

@app.route('/admin_join_game/<int:game_id>')
def admin_join_game(game_id):
    if not session.get('is_admin'):
        flash('Admin access required')
        return redirect(url_for('index'))
    
    game = Game.query.get_or_404(game_id)
    
    # Create admin user if it doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
    
    # Check if admin is already in the game
    existing_player = GamePlayer.query.filter_by(game_id=game.id, user_id=admin_user.id).first()
    if not existing_player:
        player = GamePlayer(game_id=game.id, user_id=admin_user.id)
        db.session.add(player)
        db.session.commit()
        flash('Admin joined the game as a player!')
    
    # Log in as admin
    login_user(admin_user)
    return redirect(url_for('game_room', game_id=game.id))

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Admin session ended')
    return redirect(url_for('index'))

@app.route('/admin_change_password', methods=['GET', 'POST'])
def admin_change_password():
    if not session.get('is_admin'):
        flash('Admin access required')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if not new_password or len(new_password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('admin_change_password'))
        if new_password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('admin_change_password'))
        # Update environment variable
        os.environ['ADMIN_PASSWORD'] = new_password
        # Update .env file if it exists
        dotenv_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(dotenv_path):
            set_key(dotenv_path, 'ADMIN_PASSWORD', new_password)
        flash('Admin password updated successfully!')
        return redirect(url_for('admin_menu'))
    return render_template('admin_change_password.html')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample challenges if they don't exist
        if Challenge.query.count() == 0:
            for challenge_text in SAMPLE_CHALLENGES:
                challenge = Challenge(description=challenge_text)
                db.session.add(challenge)
            db.session.commit()
    
    # Development only - Vercel handles production
    app.run(debug=True) 