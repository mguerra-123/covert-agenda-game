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
    "Get another player to spell any word out loud.",
    "Get another player to yawn right after you do.",
    "Get another player to say \"thank you\" to you.",
    "Get another player to look up information for you on their phone.",
    "Get another player to correct an obviously false statement you make.",
    "Get another player to hold your phone for you.",
    "Get another player to give you a high-five.",
    "Get another player to ask \"What?\" after you say something to them.",
    "Get another player to agree with a ridiculous statement you make.",
    "Get another player to say they remember something from the past you bring up.",
    "Get another player to ask you what time it is.",
    "Get another player to hand you a piece of their food.",
    "Get another player to correct your pronunciation of a word.",
    "Get another player to say the name of a celebrity.",
    "Get another player to shield their eyes from the sun.",
    "Get another player to show you a photo on their phone.",
    "Get another player to say \"bless you\" after you fake a sneeze.",
    "Get another player to point at something in the sky.",
    "Get another player to recommend a movie or TV show to you.",
    "Get another player to say the word \"literally.\"",
    "Get another player to scratch an itch.",
    "Get another player to agree that a certain food is overrated.",
    "Get another player to use hand sanitizer.",
    "Get another player to look at the bottom of their shoe.",
    "Get another player to sing a line from any song.",
    "Get another player to say the name of a color.",
    "Get another player to adjust their glasses or hair.",
    "Get another player to tell you a joke.",
    "Get another player to ask if you are okay.",
    "Get another player to mention a brand name.",
    "Get another player to cross their arms.",
    "Get another player to say a number greater than ten.",
    "Get another player to let you borrow a pen.",
    "Get another player to look inside their own wallet or purse.",
    "Get another player to talk about the weather.",
    "Get another player to crack their knuckles.",
    "Get another player to say your name.",
    "Get another player to refer to a pet.",
    "Get another player to take a sip of their drink.",
    "Get another player to put their phone face down on a table.",
    "Get another player to say \"I don't know.\"",
    "Get another player to stretch their arms.",
    "Get another player to name a capital city.",
    "Get another player to mention something they have to do later.",
    "Get another player to check their watch or phone for the time.",
    "Get another player to say \"I'm tired.\"",
    "Get another player to refer to a family member.",
    "Get another player to complain about something.",
    "Get another player to laugh at something that wasn't funny.",
    "Get another player to guess your age.",
    "Get another player to use a piece of slang correctly.",
    "Get another player to say the word \"weird.\"",
    "Get another player to offer you advice.",
    "Get another player to raise their eyebrows.",
    "Get another player to talk about a dream they had.",
    "Get another player to take off a jacket or sweater.",
    "Get another player to say \"that makes sense.\"",
    "Get another player to compliment someone other than you.",
    "Get another player to mention a holiday.",
    "Get another player to lean back in their chair.",
    "Get another player to say the word \"actually.\"",
    "Get another player to fold a piece of paper.",
    "Get another player to ask for your opinion.",
    "Get another player to say something in a different language.",
    "Get another player to lock their phone.",
    "Get another player to admit they were wrong about something.",
    "Get another player to say \"oh my god.\"",
    "Get another player to move an object on the table.",
    "Get another player to use a movie quote.",
    "Get another player to nod in agreement.",
    "Get another player to wipe their hands on their pants.",
    "Get another player to say \"I'm hungry.\"",
    "Get another player to recommend a restaurant.",
    "Get another player to tap their fingers on a surface.",
    "Get another player to look out a window.",
    "Get another player to say \"wait.\"",
    "Get another player to name a type of animal.",
    "Get another player to say \"seriously?\"",
    "Get another player to rub their eyes.",
    "Get another player to say something positive about themselves.",
    "Get another player to clean their glasses.",
    "Get another player to say the word \"maybe.\"",
    "Get another player to ask you to repeat yourself.",
    "Get another player to touch their face.",
    "Get another player to say the full name of another player.",
    "Get another player to talk about their job or school.",
    "Get another player to say a word that rhymes with \"cat.\"",
    "Get another player to shake their head no.",
    "Get another player to say \"that's crazy.\"",
    "Get another player to tell you to be quiet (playfully).",
    "Get another player to use a filter on a photo.",
    "Get another player to say \"I need to...\"",
    "Get another player to give you directions.",
    "Get another player to look at your shoes.",
    "Get another player to hum a tune.",
    "Get another player to say the word \"awesome.\"",
    "Get another player to sit on the floor.",
    "Get another player to talk about sports.",
    "Get another player to say \"I forgot.\"",
    "Get another player to help you look for something you \"lost.\"",
    "Get another player to say \"good morning\" or \"good night.\"",
    "Get another player to say a food they dislike.",
    "Get another player to put their hands in their pockets.",
    "Get another player to say \"it's cold\" or \"it's hot.\"",
    "Get another player to use an emoji in a text to you.",
    "Get another player to say the word \"like\" more than three times in one sentence.",
    "Get another player to point with their lips or chin.",
    "Get another player to say \"I'm bored.\"",
    "Get another player to guess a number you're thinking of.",
    "Get another player to roll their eyes.",
    "Get another player to say \"let's go.\"",
    "Get another player to say the name of a musical instrument.",
    "Get another player to take a selfie.",
    "Get another player to say \"here you go.\"",
    "Get another player to draw a shape.",
    "Get another player to say a word with three syllables.",
    "Get another player to talk about social media.",
    "Get another player to say \"I agree.\"",
    "Get another player to try to do an impression of someone.",
    "Get another player to say \"for real.\"",
    "Get another player to ask you a question about yourself.",
    "Get another player to say the name of a fruit.",
    "Get another player to shush someone.",
    "Get another player to say \"I'm sorry.\"",
    "Get another player to stand on one foot.",
    "Get another player to say \"that's hilarious.\"",
    "Get another player to talk about their childhood.",
    "Get another player to say the word \"whatever.\"",
    "Get another player to open a door for someone.",
    "Get another player to say \"I'm so full.\"",
    "Get another player to name a type of tree.",
    "Get another player to say \"I have an idea.\"",
    "Get another player to make a pun.",
    "Get another player to say a day of the week.",
    "Get another player to talk about a celebrity couple.",
    "Get another player to say \"you're right.\"",
    "Get another player to help you with a task.",
    "Get another player to say the word \"obviously.\"",
    "Get another player to whistle.",
    "Get another player to talk about their plans for the weekend.",
    "Get another player to say \"no way.\"",
    "Get another player to name a brand of car.",
    "Get another player to say \"good luck.\"",
    "Get another player to show you a video on their phone.",
    "Get another player to say \"I'm confused.\"",
    "Get another player to snap their fingers.",
    "Get another player to name a piece of furniture.",
    "Get another player to say \"I promise.\"",
    "Get another player to say something sarcastic.",
    "Get another player to talk about a recent news event.",
    "Get another player to say \"oh, interesting.\"",
    "Get another player to clap their hands.",
    "Get another player to name a body of water.",
    "Get another player to say \"I told you so.\"",
    "Get another player to use a hand gesture while talking.",
    "Get another player to say the name of a country.",
    "Get another player to ask \"why?\"",
    "Get another player to talk about a book.",
    "Get another player to say \"never mind.\"",
    "Get another player to name a type of clothing.",
    "Get another player to say \"that's a good point.\"",
    "Get another player to do a thumbs-up.",
    "Get another player to say a month of the year.",
    "Get another player to say \"I'm excited.\"",
    "Get another player to talk about a personal goal.",
    "Get another player to say the word \"amazing.\"",
    "Get another player to cover their mouth when they laugh.",
    "Get another player to say the word \"but.\"",
    "Get another player to name a superhero.",
    "Get another player to say \"I have to go.\"",
    "Get another player to refer to a fictional character.",
    "Get another player to say \"are you kidding me?\"",
    "Get another player to fix something that is crooked.",
    "Get another player to name a type of bird.",
    "Get another player to say \"that's true.\"",
    "Get another player to help you spell a difficult word.",
    "Get another player to say \"I love this song.\"",
    "Get another player to talk about a past vacation.",
    "Get another player to say the word \"definitely.\"",
    "Get another player to look up at the ceiling.",
    "Get another player to name a historical figure.",
    "Get another player to say \"I'm not sure.\"",
    "Get another player to talk about a specific app on their phone.",
    "Get another player to say \"that's weird.\"",
    "Get another player to close a tab on their computer or phone.",
    "Get another player to say \"can you help me?\"",
    "Get another player to name a type of flower.",
    "Get another player to say \"I'm proud of you.\"",
    "Get another player to talk about their favorite movie.",
    "Get another player to say the word \"so.\"",
    "Get another player to pretend to be a character.",
    "Get another player to say \"it depends.\"",
    "Get another player to name a type of dessert.",
    "Get another player to say \"I wish.\"",
    "Get another player to talk about their morning routine.",
    "Get another player to say \"I see.\"",
    "Get another player to pat someone on the back.",
    "Get another player to name a tool.",
    "Get another player to say \"you know what I mean?\"",
    "Get another player to talk about a current trend.",
    "Get another player to say \"that's impressive.\"",
    "Get another player to try and fail to do something.",
    "Get another player to say the word \"okay.\"",
    "Get another player to name a fast-food chain.",
    "Get another player to say \"I'm just kidding.\"",
    "Get another player to talk about something they bought recently.",
    "Get another player to say \"I can't believe it.\"",
    "Get another player to try a food you offer them.",
    "Get another player to name a planet.",
    "Get another player to say \"let me see.\"",
    "Get another player to talk about a personal fear.",
    "Get another player to say \"that's a good question.\"",
    "Get another player to mime an action.",
    "Get another player to name a board game.",
    "Get another player to say \"I'm in.\"",
    "Get another player to talk about their favorite season.",
    "Get another player to say \"I'll be right back.\"",
    "Get another player to try to remember someone's name.",
    "Get another player to name a type of sport.",
    "Get another player to say \"I have no idea.\"",
    "Get another player to talk about a funny memory.",
    "Get another player to say \"that's not fair.\"",
    "Get another player to use an acronym in conversation (e.g., LOL, OMG).",
    "Get another player to name a type of cheese.",
    "Get another player to say \"I'm ready.\"",
    "Get another player to talk about their pet peeves.",
    "Get another player to say \"you're welcome.\"",
    "Get another player to hide something in their hand.",
    "Get another player to name a mythical creature.",
    "Get another player to say \"I knew it!\"",
    "Get another player to talk about a talent they have.",
    "Get another player to say \"that's enough.\"",
    "Get another player to say a word backwards.",
    "Get another player to name a brand of soda.",
    "Get another player to say \"I'm on my way.\"",
    "Get another player to talk about something they learned recently.",
    "Get another player to say \"don't worry about it.\"",
    "Get another player to try to catch something you throw.",
    "Get another player to name a cartoon character.",
    "Get another player to say \"I'm not feeling well.\"",
    "Get another player to talk about a song stuck in their head.",
    "Get another player to say \"are you serious?\"",
    "Get another player to move out of someone's way.",
    "Get another player to name a kitchen appliance.",
    "Get another player to say \"I'll do it later.\"",
    "Get another player to talk about their dream job.",
    "Get another player to say \"that's what she said.\"",
    "Get another player to use a calculator.",
    "Get another player to name a famous landmark.",
    "Get another player to say \"I'm listening.\"",
    "Get another player to talk about something they are looking forward to.",
    "Get another player to say \"I'm going to...\"",
    "Get another player to try to solve a riddle you tell them.",
    "Get another player to name a shape.",
    "Get another player to say \"I don't care.\"",
    "Get another player to talk about their favorite animal.",
    "Get another player to say \"that's so cool.\"",
    "Get another player to wipe a surface clean.",
    "Get another player to name a type of weather.",
    "Get another player to say \"I'm almost done.\"",
    "Get another player to talk about a video game.",
    "Get another player to say \"it's not a big deal.\"",
    "Get another player to put on headphones.",
    "Get another player to name a historical event.",
    "Get another player to say \"let's do it.\"",
    "Get another player to talk about their favorite book.",
    "Get another player to say \"I can't wait.\"",
    "Get another player to start a timer or stopwatch.",
    "Get another player to name a geometric shape.",
    "Get another player to say \"I don't think so.\"",
    "Get another player to talk about their commute.",
    "Get another player to say \"what are you doing?\"",
    "Get another player to check the ingredients on a food package.",
    "Get another player to name a vegetable.",
    "Get another player to say \"I'll try.\"",
    "Get another player to talk about a funny video they saw.",
    "Get another player to say \"that sounds good.\"",
    "Get another player to search for something in a bag.",
    "Get another player to name an insect.",
    "Get another player to say \"I'm not a fan.\"",
    "Get another player to talk about a political topic.",
    "Get another player to say \"that's a shame.\"",
    "Get another player to charge their phone.",
    "Get another player to name a type of drink.",
    "Get another player to say \"I'm not surprised.\"",
    "Get another player to talk about their favorite band or artist.",
    "Get another player to say \"I guess so.\"",
    "Get another player to pick something up off the floor.",
    "Get another player to name a type of shoe.",
    "Get another player to say \"it is what it is.\"",
    "Get another player to talk about a weird dream.",
    "Get another player to say \"what's the plan?\"",
    "Get another player to use a foreign accent.",
    "Get another player to name a part of the human body.",
    "Get another player to say \"I'm so sorry.\"",
    "Get another player to talk about their first job.",
    "Get another player to say \"that's a good one.\"",
    "Get another player to try to fix something that is broken.",
    "Get another player to say a word that starts with the letter 'P'.",
    "Get another player to say \"I need help.\"",
    "Get another player to talk about their favorite holiday.",
    "Get another player to say \"are you sure?\"",
    "Get another player to shuffle a deck of cards.",
    "Get another player to name a type of pasta.",
    "Get another player to say \"I don't get it.\"",
    "Get another player to talk about something they regret.",
    "Get another player to say \"that's adorable.\"",
    "Get another player to turn a light on or off.",
    "Get another player to name a type of dog.",
    "Get another player to say \"I'm out of here.\"",
    "Get another player to talk about a favorite teacher.",
    "Get another player to say \"I'll take it.\"",
    "Get another player to say the alphabet.",
    "Get another player to name a type of candy.",
    "Get another player to say \"I don't remember.\"",
    "Get another player to talk about their favorite app.",
    "Get another player to say \"that's a good idea.\"",
    "Get another player to look under a table.",
    "Get another player to name a Disney character.",
    "Get another player to say \"I'm not in the mood.\"",
    "Get another player to talk about a childhood memory.",
    "Get another player to say \"you first.\"",
    "Get another player to use a remote control.",
    "Get another player to name a type of fish.",
    "Get another player to say \"I don't believe you.\"",
    "Get another player to talk about their best friend.",
    "Get another player to say \"that's my favorite.\"",
    "Get another player to close a window or door.",
    "Get another player to name a type of weather phenomenon.",
    "Get another player to say \"I'm working on it.\"",
    "Get another player to talk about a conspiracy theory.",
    "Get another player to say \"I'll think about it.\"",
    "Get another player to do a coin toss.",
    "Get another player to name a famous scientist.",
    "Get another player to say \"I have a question.\"",
    "Get another player to talk about their exercise routine.",
    "Get another player to say \"that's a relief.\"",
    "Get another player to compare two things.",
    "Get another player to name a piece of art.",
    "Get another player to say \"I'm freezing.\"",
    "Get another player to talk about a viral trend.",
    "Get another player to say \"I'm all ears.\"",
    "Get another player to look at a map.",
    "Get another player to name a famous author.",
    "Get another player to say \"that's a tough one.\"",
    "Get another player to talk about their biggest accomplishment.",
    "Get another player to say \"I'm so happy for you.\"",
    "Get another player to count objects in a room.",
    "Get another player to name a famous building.",
    "Get another player to say \"I need a break.\"",
    "Get another player to talk about something they are grateful for.",
    "Get another player to say \"you're a lifesaver.\"",
    "Get another player to play rock-paper-scissors with you.",
    "Get another player to name a type of vehicle.",
    "Get another player to say \"that's my jam.\"",
    "Get another player to talk about their favorite restaurant.",
    "Get another player to say \"I'm sweating.\"",
    "Get another player to try to read your mind.",
    "Get another player to name a type of fabric.",
    "Get another player to say \"I can't complain.\"",
    "Get another player to talk about a public figure.",
    "Get another player to say \"that's hilarious.\"",
    "Get another player to open a jar or bottle for you.",
    "Get another player to name a type of jewelry.",
    "Get another player to say \"I'm not going to lie.\"",
    "Get another player to talk about their favorite scent.",
    "Get another player to say \"that's the spirit.\"",
    "Get another player to look at their reflection.",
    "Get another player to name a constellation.",
    "Get another player to say \"I'm dead.\" (as a figure of speech)",
    "Get another player to talk about their favorite childhood toy.",
    "Get another player to say \"you're the best.\"",
    "Get another player to try to balance something on their finger.",
    "Get another player to say a type of sauce.",
    "Get another player to say \"I need coffee.\"",
    "Get another player to talk about their favorite TV show.",
    "Get another player to say \"that's a classic.\"",
    "Get another player to try to say a tongue twister.",
    "Get another player to name a social media platform.",
    "Get another player to say \"I'll pass.\"",
    "Get another player to talk about a memorable gift they received.",
    "Get another player to say \"that's understandable.\"",
    "Get another player to untangle a cord or string.",
    "Get another player to name a type of soup.",
    "Get another player to say \"I'm starving.\"",
    "Get another player to talk about their favorite color.",
    "Get another player to say \"that's the goal.\"",
    "Get another player to make a shadow puppet.",
    "Get another player to name a type of nut.",
    "Get another player to say \"I'm speechless.\"",
    "Get another player to talk about their favorite place in the world.",
    "Get another player to say \"you've got to be kidding.\"",
    "Get another player to write their name down.",
    "Get another player to name a brand of cereal.",
    "Get another player to say \"I'll be there.\"",
    "Get another player to talk about a secret they have.",
    "Get another player to say \"that's my cue.\"",
    "Get another player to try to whistle with their fingers.",
    "Get another player to name a famous artist.",
    "Get another player to say \"I'm not picky.\"",
    "Get another player to talk about a time they were embarrassed.",
    "Get another player to say \"that's for sure.\"",
    "Get another player to organize a small pile of items.",
    "Get another player to name a type of hat.",
    "Get another player to say \"I'm impressed.\"",
    "Get another player to talk about their family traditions.",
    "Get another player to say \"you read my mind.\"",
    "Get another player to make an animal sound.",
    "Get another player to name a type of spice.",
    "Get another player to say \"I'm all set.\"",
    "Get another player to talk about a skill they want to learn.",
    "Get another player to say \"that's the dream.\"",
    "Get another player to check if they have something in their teeth.",
    "Get another player to name a famous activist.",
    "Get another player to say \"I can't.\"",
    "Get another player to talk about their favorite comedian.",
    "Get another player to say \"you're hilarious.\"",
    "Get another player to build a small tower out of objects.",
    "Get another player to name a type of bread.",
    "Get another player to say \"I'm so over it.\"",
    "Get another player to talk about a strange food they've eaten.",
    "Get another player to say \"that's the truth.\"",
    "Get another player to look at the sky and comment on the clouds.",
    "Get another player to name a famous inventor.",
    "Get another player to say \"I can relate.\"",
    "Get another player to talk about their favorite holiday movie.",
    "Get another player to say \"you get what I'm saying?\"",
    "Get another player to perform a simple magic trick.",
    "Get another player to name a type of beer or wine.",
    "Get another player to say \"I'm not a morning person.\"",
    "Get another player to talk about a cause they support.",
    "Get another player to say \"that's a bold move.\"",
    "Get another player to look for a specific object in the room.",
    "Get another player to name a famous athlete.",
    "Get another player to say \"I'm on the fence.\"",
    "Get another player to talk about their favorite thing about themselves.",
    "Get another player to say \"you nailed it.\"",
    "Get another player to try to speak in a low or high-pitched voice.",
    "Get another player to name a type of tea.",
    "Get another player to say \"I'm so confused.\"",
    "Get another player to talk about a recurring dream.",
    "Get another player to say \"that's a good memory.\"",
    "Get another player to demonstrate a dance move.",
    "Get another player to say a word that rhymes with \"blue\".",
    "Get another player to say \"let me check.\"",
    "Get another player to talk about a piece of technology they can't live without.",
    "Get another player to say \"that's the way to do it.\"",
    "Get another player to try to guess a song you're humming.",
    "Get another player to name a type of farm animal.",
    "Get another player to say \"I'm not so sure about that.\"",
    "Get another player to talk about their morning coffee routine.",
    "Get another player to say \"you're a genius.\"",
    "Get another player to try to juggle.",
    "Get another player to name a type of pizza topping.",
    "Get another player to say \"I'm going crazy.\"",
    "Get another player to talk about a time they got lost.",
    "Get another player to say \"that's a good sign.\"",
    "Get another player to tell you the day's date.",
    "Get another player to name a famous director.",
    "Get another player to say \"I'm in a good mood.\"",
    "Get another player to talk about their favorite podcast.",
    "Get another player to say \"you're making me blush.\"",
    "Get another player to try to pat their head and rub their stomach.",
    "Get another player to name a type of ocean animal.",
    "Get another player to say \"I need a vacation.\"",
    "Get another player to talk about their favorite season and why.",
    "Get another player to say \"that's a game changer.\"",
    "Get another player to tell you which way is North.",
    "Get another player to name a character from a classic book.",
    "Get another player to say \"I'm not worried.\"",
    "Get another player to talk about their favorite type of weather.",
    "Get another player to say \"you're on fire.\"",
    "Get another player to try to estimate the length of an object.",
    "Get another player to name a type of cookie.",
    "Get another player to say \"I'm just saying.\"",
    "Get another player to talk about a road trip they've taken.",
    "Get another player to say \"that's a good way to put it.\"",
    "Get another player to make a paper airplane.",
    "Get another player to say a word with four syllables.",
    "Get another player to say \"I'm trying my best.\"",
    "Get another player to talk about their favorite board game.",
    "Get another player to say \"that's out of my control.\"",
    "Get another player to try to name all the players in the game.",
    "Get another player to name a type of mountain.",
    "Get another player to say \"I'm not a fan of that.\"",
    "Get another player to talk about a time they were very lucky.",
    "Get another player to say \"that's the whole point.\"",
    "Get another player to try to wink with both eyes.",
    "Get another player to name a part of a car.",
    "Get another player to say \"I'm feeling lucky.\"",
    "Get another player to talk about their favorite YouTuber.",
    "Get another player to say \"you've got a point.\"",
    "Get another player to try to remember a specific date.",
    "Get another player to name a type of river.",
    "Get another player to say \"I'm not complaining.\"",
    "Get another player to talk about a movie that made them cry.",
    "Get another player to say \"that's a different story.\"",
    "Get another player to try to impersonate another player.",
    "Get another player to name a brand of clothing.",
    "Get another player to say \"I'm taking a break.\"",
    "Get another player to talk about a food they want to try.",
    "Get another player to say \"that's a great question.\"",
    "Get another player to try to identify a smell with their eyes closed.",
    "Get another player to name a famous painting.",
    "Get another player to say \"I'm not convinced.\"",
    "Get another player to talk about a concert they've been to.",
    "Get another player to say \"you're too kind.\"",
    "Get another player to try to say \"red leather, yellow leather\" five times fast.",
    "Get another player to name a type of house.",
    "Get another player to say \"I'm running on empty.\"",
    "Get another player to talk about their favorite dessert.",
    "Get another player to say \"that's a nice thought.\"",
    "Get another player to try to guess your middle name.",
    "Get another player to name a famous philosopher.",
    "Get another player to say \"I'm not ready for this.\"",
    "Get another player to talk about a memorable meal.",
    "Get another player to say \"you're my hero.\"",
    "Get another player to try to make a noise using only their mouth.",
    "Get another player to name a type of bridge.",
    "Get another player to say \"I'm not the one to ask.\"",
    "Get another player to talk about a piece of good advice they received.",
    "Get another player to say \"that's a weight off my shoulders.\"",
    "Get another player to try to guess your favorite color.",
    "Get another player to name a famous poem.",
    "Get another player to say \"I'm not judging.\"",
    "Get another player to talk about a time they helped someone.",
    "Get another player to say \"you're a good sport.\"",
    "Get another player to try to fold a t-shirt perfectly.",
    "Get another player to say a type of sandwich.",
    "Get another player to say \"I'm having a great time.\"",
    "Get another player to talk about their favorite place to relax.",
    "Get another player to say \"that's a pleasant surprise.\"",
    "Get another player to try to identify a song from its first second.",
    "Get another player to name a type of musical genre.",
    "Get another player to say \"I'm not going anywhere.\"",
    "Get another player to talk about a subject they know a lot about.",
    "Get another player to say \"you're in my thoughts.\"",
    "Get another player to try to hold their breath for 20 seconds.",
    "Get another player to name a type of currency.",
    "Get another player to say \"I'm keeping my options open.\"",
    "Get another player to talk about their favorite cartoon.",
    "Get another player to say \"that's a work of art.\"",
    "Get another player to try to find a four-leaf clover.",
    "Get another player to name a type of cloud.",
    "Get another player to say \"I'm not making any promises.\"",
    "Get another player to talk about a weird food combination they like.",
    "Get another player to say \"you're asking the right person.\"",
    "Get another player to try to remember their first memory.",
    "Get another player to name a type of dance.",
    "Get another player to say \"I'm having deja vu.\"",
    "Get another player to talk about a favorite family recipe.",
    "Get another player to say \"that's a blast from the past.\"",
    "Get another player to try to estimate the temperature.",
    "Get another player to say the name of a US state.",
    "Get another player to say \"I'm not a robot\" and mean it.",
    "Get another player to talk about a time they faced a fear.",
    "Get another player to say \"you're on the right track.\"",
    "Get another player to try to say a difficult name correctly.",
    "Get another player to name a famous historical battle.",
    "Get another player to say \"I'm not a people person.\"",
    "Get another player to talk about a good deed they did.",
    "Get another player to say \"that's the best I can do.\"",
    "Get another player to try to tell a story without using the word \"the\".",
    "Get another player to name a type of government.",
    "Get another player to say \"I'm not holding my breath.\"",
    "Get another player to talk about a funny misunderstanding.",
    "Get another player to say \"you've made my day.\"",
    "Get another player to try to name five things that are blue.",
    "Get another player to name a famous scientist's discovery.",
    "Get another player to say \"I'm not one to gossip, but...\"",
    "Get another player to talk about a favorite childhood book.",
    "Get another player to say \"that's a beautiful thing.\"",
    "Get another player to try to come up with a team name for the group.",
    "Get another player to name a type of building material.",
    "Get another player to say \"I'm not going to argue.\"",
    "Get another player to talk about a personal mantra or philosophy.",
    "Get another player to say \"you're a natural.\"",
    "Get another player to try to remember what they ate for breakfast.",
    "Get another player to say the name of an ocean.",
    "Get another player to say \"I'm not a fan of surprises.\"",
    "Get another player to talk about a project they are proud of.",
    "Get another player to say \"that's a sign.\"",
    "Get another player to try to find a specific word in a book.",
    "Get another player to name a famous speech.",
    "Get another player to say \"I'm not in a rush.\"",
    "Get another player to talk about a time they felt powerful.",
    "Get another player to say \"you're an inspiration.\"",
    "Get another player to try to guess a password you made up.",
    "Get another player to name a type of reptile.",
    "Get another player to say \"I'm not giving up.\"",
    "Get another player to talk about their favorite smell.",
    "Get another player to say \"that's a deal.\"",
    "Get another player to try to create a new handshake with you.",
    "Get another player to name a famous explorer.",
    "Get another player to say \"I'm not superstitious.\"",
    "Get another player to talk about a time they were completely wrong.",
    "Get another player to say \"you're a true friend.\"",
    "Get another player to try to draw a perfect circle.",
    "Get another player to say the name of a jungle animal.",
    "Get another player to say \"I'm not in control.\"",
    "Get another player to talk about a place they want to visit.",
    "Get another player to say \"that's a good thing to know.\"",
    "Get another player to try to guess the last movie you watched.",
    "Get another player to name a type of rock or mineral.",
    "Get another player to say \"I'm not in the mood for games.\" (The irony!)",
    "Get another player to talk about a time they got lucky.",
    "Get another player to say \"you're on a roll.\"",
    "Get another player to try to tell a lie and a truth, and have you guess.",
    "Get another player to name a famous politician.",
    "Get another player to say \"I'm not looking for trouble.\"",
    "Get another player to talk about a favorite photograph they have.",
    "Get another player to say \"that's a load off my mind.\"",
    "Get another player to try to say the months of the year backwards.",
    "Get another player to name a famous landmark they've visited.",
    "Get another player to say \"I'm not going to say anything.\"",
    "Get another player to talk about a favorite piece of clothing they own.",
    "Get another player to say \"you're a mind reader.\"",
    "Get another player to try to build a house of cards.",
    "Get another player to say the name of a desert animal.",
    "Get another player to say \"I'm not taking sides.\"",
    "Get another player to talk about a time they were proud of someone else.",
    "Get another player to say \"that's the whole point.\"",
    "Get another player to try to guess what's in your pocket.",
    "Get another player to name a famous revolutionary.",
    "Get another player to say \"I'm not trying to be difficult.\"",
    "Get another player to talk about a favorite TV show from their childhood.",
    "Get another player to say \"you're full of surprises.\"",
    "Get another player to try to remember a phone number by heart.",
    "Get another player to name a type of weather storm.",
    "Get another player to say \"I'm not that kind of person.\"",
    "Get another player to talk about a time they learned a valuable lesson.",
    "Get another player to say \"that's a wrap.\"",
    "Get another player to try to make a rhyme with your name.",
    "Get another player to name a famous king or queen.",
    "Get another player to say \"I'm not the boss.\"",
    "Get another player to talk about their favorite way to spend a rainy day.",
    "Get another player to say \"you're a legend.\"",
    "Get another player to try to find the North Star.",
    "Get another player to name a type of body organ.",
    "Get another player to say \"I'm not made of money.\"",
    "Get another player to talk about a time they felt truly happy.",
    "Get another player to say \"that's a work in progress.\"",
    "Get another player to try to find a specific shape in the clouds.",
    "Get another player to name a famous battle.",
    "Get another player to say \"I'm not interested.\"",
    "Get another player to talk about a time they overcame an obstacle.",
    "Get another player to say \"you're the only one who gets it.\"",
    "Get another player to try to name every other player's favorite color.",
    "Get another player to name a type of fish you can eat.",
    "Get another player to say \"I'm not in charge.\"",
    "Get another player to talk about a time they felt brave.",
    "Get another player to say \"that's above my pay grade.\"",
    "Get another player to try to guess the meaning of an obscure word.",
    "Get another player to name a famous queen.",
    "Get another player to say \"I'm not a threat.\"",
    "Get another player to talk about their favorite thing about the current season.",
    "Get another player to say \"you're a sight for sore eyes.\"",
    "Get another player to try to write with their non-dominant hand.",
    "Get another player to name a famous novel.",
    "Get another player to say \"I'm not looking forward to it.\"",
    "Get another player to talk about a moment that changed their life.",
    "Get another player to say \"that's a good way to be.\"",
    "Get another player to try to tell time by the sun.",
    "Get another player to name a famous play.",
    "Get another player to say \"I'm not moving.\"",
    "Get another player to talk about a time they made a big mistake.",
    "Get another player to say \"you're one of a kind.\"",
    "Get another player to try to guess the year a coin was minted.",
    "Get another player to name a famous composer.",
    "Get another player to say \"I'm not a role model.\"",
    "Get another player to talk about a time they felt understood.",
    "Get another player to say \"that's all I'm saying.\"",
    "Get another player to try to find a specific constellation.",
    "Get another player to name a famous sculptor.",
    "Get another player to say \"I'm not a fortune teller.\"",
    "Get another player to talk about a favorite memory with their family.",
    "Get another player to say \"you're a miracle worker.\"",
    "Get another player to try to identify a brand by its logo alone."
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