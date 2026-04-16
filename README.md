# 🤫 Blurmoji

## Concept
On each round, the player must guess the random emoji hidden behind the pixelated-blurry image.<br>
He has at his disposal the entire emoji set to guess the hidden emoji.<br>
Every time he guesses wrong, the reference image increases in resolution, in order to make it less blurry and make it easier on the player.

## Game modes
- v1 : Daily challenge
  - 5 guesses maximum
  - challenge once a day only
- v2 : Endless mode
  - try to get the highest streak (=consecutive wins)
  - 1 guess max per round
- v2 : Time crunch
  - try to get the highest streak (=consecutive wins)
  - unlimited guesses, can skip
  - 60 seconds

## Design
Modern and minimalist look <br>
Dark grey overall, with round edges for components, Roboto police<br>
Only includes header (to pick different game modes, return to main menu and leaderboard) and body of game.<br>
The body of the game contains vertically :
- the blurred emoji image
- the past guesses among the 5 total guesses
- the keyboard UI listing all emojis in their respective groups

## Code practices
- Python backend purely (something like NiceGUI), only a simple web server to serve the game and handle API requests
- Minimalist and clean code, no comments and no docstrings when possible - code should be self-explanatory
- Classes and functions should be as small as possible, with a single responsibility, and type hints
- Design patterns when possible, especially for the game logic and state management
- Persistence to allow different database connections, use an ORM for database interactions

## Project Structure
```
src/
├── core/                    # Core utilities and services
│   └── services/           # Service classes (emoji_kitchen_service.py)
├── gameplay/               # Game logic and modes
│   ├── modes/             # Game mode implementations
│   └── state/             # Game state management
├── api/                   # API gateway and routes
│   ├── gateway/          # Web server abstraction
│   └── routes/           # API route handlers
├── persistence/           # Database abstraction layer
└── frontend/              # Frontend (to be implemented later)
```

## Configuration
Configuration is managed in `src/config/config.py` (imported via package `src.config`):
- `EMOJI_KITCHEN_METADATA_URL`: URL for emoji metadata (Google Emoji Kitchen API)
- `REQUEST_TIMEOUT`: HTTP request timeout in seconds (10)

## Caching
Emoji metadata is automatically cached locally in `.game_state/emoji_metadata_cache.json`:
- First run fetches from remote API and saves locally
- Subsequent runs load from cache for faster startup
- Cache persists between application restarts
