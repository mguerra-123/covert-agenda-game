# Covert Agenda

A web-based multiplayer social deception game inspired by "Don't Get Got" where players complete secret missions without getting caught!

## Features

- **Admin-controlled gameplay**: Only admins can create games and manage settings
- **Customizable veto system**: Admins can set how many challenges players can skip
- **QR code generation**: Easy game joining with scannable QR codes
- **Real-time challenge system**: Players receive individual secret missions
- **Admin play mode**: Admins can join and play in their own games
- **Modern UI**: Beautiful dark theme with glassmorphism design

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Access the game**:
   - Open your browser to `http://localhost:5000`
   - Use the admin password (default: `admin123`) to access admin controls
   - Create a new game with custom settings
   - Share the QR code or game code with players

## How to Play

1. **Admin Setup**:
   - Login with admin password
   - Create a new game with custom veto limits
   - Share the generated QR code with players

2. **Player Joining**:
   - Scan the QR code or enter the game code
   - Players automatically receive secret challenges

3. **Gameplay**:
   - Complete missions stealthily without getting caught
   - Use vetoes to skip difficult challenges (limited by admin settings)
   - Mark challenges as complete, failed, or vetoed

4. **Game End**:
   - Only admins can end the game
   - Winner is determined by most completed challenges
   - Full statistics are displayed

## Admin Features

- **Game Creation**: Set game name and veto limits
- **QR Code Generation**: Automatic QR codes for easy joining
- **Password Management**: Change admin password securely
- **Game Management**: View all games and join as player
- **Admin Play**: Participate in games while maintaining admin control

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Font Awesome, Custom CSS
- **Database**: SQLite (with PostgreSQL support for production)
- **QR Codes**: qrcode library with PIL
- **Deployment**: Gunicorn, Heroku/Railway ready

## File Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/               # Static assets
│   ├── css/style.css     # Custom styles
│   └── js/main.js        # JavaScript functionality
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── admin_menu.html   # Admin interface
│   ├── game_room.html    # Game interface
│   └── ...               # Other templates
└── instance/             # Database files
    └── game.db           # SQLite database
```

## Deployment

The application is ready for deployment on platforms like:
- **Heroku**: Use the included Procfile
- **Railway**: Automatic deployment from GitHub
- **Render**: Use the health check endpoint
- **Vercel**: Serverless deployment

## Environment Variables

- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `ADMIN_PASSWORD`: Admin access password

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

---

**Have fun playing Covert Agenda with your friends!** 🎭 