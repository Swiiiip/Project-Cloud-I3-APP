# 🤫 Blurmoji

## Concept
On each play, the player must guess the random emoji hidden behind the pixelated-blurry image.<br>
He has at his disposal the entire emoji set to guess the hidden emoji.<br>
Every time he guesses wrong, the reference image increases in resolution, in order to make it less blurry and make it easier on the player.

## Game modes
- v1 : Daily challenge
  - 5 guesses maximum
  - challenge once a day only
- v2 : Hardcore
  - try to get the highest streak (=consecutive wins)
  - 1 guess max per play
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
- Python backend and frontend if possible
- Minimalist and clean code, no comments and no docstrings when possible - code should be self-explanatory
- Classes and functions should be as small as possible, with a single responsibility, and type hints
- Design patterns when possible, especially for the game logic and state management
- Persistence to allow different database connections, use an ORM for database interactions