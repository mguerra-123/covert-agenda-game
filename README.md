# Covert Agenda - Multiplayer Challenge Game

A web-based multiplayer game where players complete social challenges while trying to avoid detection. Features admin controls and a retro cyberpunk aesthetic.

## 🎮 Two Versions Available

### Simple Version (`simple-version` branch)
- **Basic admin controls** for game management
- **Open-ended gameplay** - admin manually ends the game
- **Customizable veto system** - set how many challenges players can skip
- **QR code generation** for easy game sharing
- **Perfect for casual play** and quick setup

### Advanced Version (`advanced-version` branch)
- **Multiple game modes**:
  - **Open-ended**: Admin decides when to end
  - **Timed**: Game automatically ends after set duration (15-300 minutes)
  - **Winner takes all**: Game ends when a player completes X challenges (3-20)
- **All features from simple version** plus advanced game mechanics
- **Automatic game ending** based on time or challenge completion
- **Progress tracking** for winner takes all mode

## 🚀 Features

- **Admin Controls**: Password-protected admin panel for game management
- **QR Code Generation**: Easy game sharing with QR codes
- **Veto System**: Players can veto challenges they find inappropriate
- **Real-time Updates**: Live challenge updates and game status
- **Retro Cyberpunk UI**: Dark purple theme with neon accents
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (with PostgreSQL support for production)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with retro cyberpunk theme
- **Authentication**: Flask-Login
- **QR Codes**: qrcode library

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/mguerra-123/covert-agenda-game.git
   cd covert-agenda-game
   ```

2. **Choose your version**
   ```bash
   # For simple version (recommended for beginners)
   git checkout simple-version
   
   # For advanced version with game modes
   git checkout advanced-version
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the game**
   - Open your browser and go to `http://127.0.0.1:5000`
   - Use admin password: `admin123` (change this in production - see deployment guide)

## 🎯 How to Play

### For Admins:
1. Login with the admin password
2. Create a new game with your preferred settings:
   - **Simple version**: Set game name and veto limits
   - **Advanced version**: Choose game mode, time limits, or challenge counts
3. Share the game code or QR code with players
4. Join the game to participate or monitor progress
5. End the game when appropriate

### For Players:
1. Join a game using the provided code or QR code
2. Receive random challenges to complete
3. Mark challenges as completed, failed, or veto them
4. Try to complete challenges without other players noticing
5. Win by completing the most challenges or meeting victory conditions

## 🎨 Customization

### Changing the Admin Password
1. Access the admin menu
2. Click "Change Admin Password"
3. Enter the current password and new password

### Adding Custom Challenges
Edit the `SAMPLE_CHALLENGES` list in `app.py` to add your own challenges.

### Styling
Modify `static/css/style.css` to customize the game's appearance.

## 🌐 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set environment variables:
   - `SECRET_KEY`: A secure random string
   - `ADMIN_PASSWORD`: Your admin password
   - `DATABASE_URL`: Your database URL (for PostgreSQL)

2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

## 📁 Project Structure

```
covert-agenda-game/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Game styling
│   └── js/
│       └── main.js       # Client-side JavaScript
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── game_room.html    # Game interface
│   └── ...               # Other templates
├── instance/             # Database files (not in git)
└── README.md            # This file
```

## 🔄 Version Management

### Switching Between Versions
```bash
# Switch to simple version
git checkout simple-version

# Switch to advanced version
git checkout advanced-version

# Switch to main branch (latest)
git checkout main
```

### Creating New Features
```bash
# Create a new feature branch from simple version
git checkout simple-version
git checkout -b feature/new-feature

# Create a new feature branch from advanced version
git checkout advanced-version
git checkout -b feature/new-feature
```

## 🤝 Contributing

1. Fork the repository
2. Choose which version to work on (simple or advanced)
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🐛 Issues

If you encounter any issues or have suggestions, please [open an issue](https://github.com/mguerra-123/covert-agenda-game/issues) on GitHub.

## 🔗 Links

- [GitHub Repository](https://github.com/mguerra-123/covert-agenda-game)
- [Simple Version](https://github.com/mguerra-123/covert-agenda-game/tree/simple-version)
- [Advanced Version](https://github.com/mguerra-123/covert-agenda-game/tree/advanced-version)
- [Live Demo](https://your-demo-url.com) (if deployed)

---

**Enjoy playing Covert Agenda!** 🕵️‍♀️✨ 