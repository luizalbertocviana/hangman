# Hangman CLI Game - System Architecture

## 1. Architecture Overview

### 1.1 Architecture Style
**Modular Monolithic Architecture**

The Hangman CLI game follows a **modular monolithic** design pattern, organized into loosely-coupled components with well-defined interfaces. This choice is justified by:

- **Single deployment unit**: CLI application runs as a standalone process
- **Shared memory space**: All components operate within the same process
- **Clear separation of concerns**: Each module has a single responsibility
- **Testability**: Modules can be unit-tested in isolation
- **Maintainability**: Changes to one module minimally impact others

### 1.2 System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER                                    │
│                         │                                    │
│                         ▼                                    │
│              ┌─────────────────────┐                         │
│              │   Terminal/Shell    │                         │
│              │   (stdin/stdout)    │                         │
│              └─────────┬───────────┘                         │
│                        │                                     │
│                        ▼                                     │
│         ┌──────────────────────────────┐                     │
│         │     HANGMAN CLI APPLICATION  │                     │
│         │                              │                     │
│         │  ┌────────────────────────┐  │                     │
│         │  │   Configuration Mgr    │  │                     │
│         │  └────────────────────────┘  │                     │
│         │                              │                     │
│         │  ┌────────────────────────┐  │                     │
│         │  │    Word List Mgr       │◄─┼───── Word Files    │
│         │  └────────────────────────┘  │                     │
│         │                              │                     │
│         │  ┌────────────────────────┐  │                     │
│         │  │     Game Engine        │  │                     │
│         │  │   (Core Logic)         │  │                     │
│         │  └────────────────────────┘  │                     │
│         │         │        │           │                     │
│         │         ▼        ▼           │                     │
│         │  ┌──────────┐ ┌──────────┐  │                     │
│         │  │   UI     │ │ Session  │  │                     │
│         │  │ Renderer │ │ Stats    │  │                     │
│         │  └──────────┘ └──────────┘  │                     │
│         └──────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Component Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         MAIN ENTRY POINT                            │
│                           (main.py)                                 │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                      APPLICATION CONTROLLER                         │
│                         (app.py)                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  - Initialize components                                      │  │
│  │  - Manage game loop                                           │  │
│  │  - Handle session lifecycle                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ CONFIGURATION │   │   GAME ENGINE   │   │  WORD LIST MGR  │
│     MGR       │   │    (Core)       │   │                 │
│               │   │                 │   │                 │
│ - Load config │   │ - Game state    │   │ - Load words    │
│ - Validate    │   │ - Guess logic   │   │ - Filter by     │
│ - Settings    │   │ - Win/Loss      │   │   difficulty    │
│   defaults    │   │ - Hangman state │   │ - Categories    │
└───────────────┘   └─────────────────┘   └─────────────────┘
        │                     │                     │
        │                     ▼                     │
        │           ┌─────────────────┐             │
        │           │   UI RENDERER   │             │
        │           │                 │             │
        │           │ - Display state │             │
        │           │ - ASCII art     │             │
        │           │ - Messages      │             │
        └──────────►│ - Input prompt  │◄────────────┘
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  INPUT HANDLER  │
                    │                 │
                    │ - Read stdin    │
                    │ - Validate      │
                    │ - Sanitize      │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ SESSION STATS   │
                    │                 │
                    │ - Track games   │
                    │ - Win/Loss      │
                    │ - Persistence   │
                    └─────────────────┘
```

### 2.2 Module Descriptions

| Module | Responsibility | Key Functions |
|--------|----------------|---------------|
| **Main Entry Point** | Application bootstrap | Parse args, start app, handle signals |
| **Application Controller** | Game session orchestration | Init, game loop, replay, exit |
| **Configuration Manager** | Settings management | Load config, validate, provide defaults |
| **Game Engine** | Core game logic | State management, guess evaluation, win/loss detection |
| **Word List Manager** | Word data access | Load words, filter by category/difficulty |
| **UI Renderer** | Terminal output | Display game state, ASCII art, messages |
| **Input Handler** | User input processing | Read, validate, sanitize input |
| **Session Statistics** | Stats tracking | Track metrics, persist to file |

---

## 3. Data Models

### 3.1 Game State

```python
class GameState:
    """Represents the current state of a game session."""
    
    word: str                    # Target word (lowercase)
    category: str                # Word category
    difficulty: Difficulty       # EASY | MEDIUM | HARD
    guessed_letters: Set[str]    # Letters guessed by player
    incorrect_guesses: int       # Count of wrong guesses (0-6)
    is_game_over: bool           # True when win or loss
    is_win: bool                 # True if player won
    start_time: datetime         # Game start timestamp
    end_time: Optional[datetime] # Game end timestamp
```

### 3.2 Session Statistics

```python
class SessionStats:
    """Tracks statistics across multiple game sessions."""
    
    games_played: int       # Total games in session
    games_won: int          # Wins in session
    games_lost: int         # Losses in session
    current_streak: int     # Current win streak
    best_streak: int        # Best win streak
    total_guesses: int      # Total guesses made
    start_time: datetime    # Session start
```

### 3.3 Word Entry

```python
class WordEntry:
    """Represents a word in the word list."""
    
    word: str               # The word itself
    category: str           # Category (animals, countries, etc.)
    difficulty: Difficulty  # Based on length/complexity
```

### 3.4 Configuration

```python
class Config:
    """Application configuration."""
    
    max_incorrect_guesses: int    # Default: 6
    word_list_path: str           # Path to word list files
    stats_file_path: str          # Path for stats persistence
    enable_colors: bool           # Terminal color support
    min_terminal_width: int       # Default: 80
    min_terminal_height: int      # Default: 24
    language: str                 # Default: 'en'
```

---

## 4. Database Schema

### 4.1 File-Based Storage

The application uses **file-based storage** for persistence:

#### Word List Files (JSON)
```json
{
  "categories": {
    "animals": {
      "easy": ["cat", "dog", "bird"],
      "medium": ["elephant", "giraffe"],
      "hard": ["chameleon", "armadillo"]
    },
    "countries": {
      "easy": ["usa", "china"],
      "medium": ["brazil", "argentina"],
      "hard": ["liechtenstein", "kyrgyzstan"]
    }
  }
}
```

#### Session Statistics (JSON)
```json
{
  "version": "1.0",
  "last_updated": "2026-03-08T12:00:00Z",
  "stats": {
    "games_played": 42,
    "games_won": 28,
    "games_lost": 14,
    "current_streak": 3,
    "best_streak": 7,
    "total_guesses": 312
  }
}
```

#### Configuration File (YAML)
```yaml
game:
  max_incorrect_guesses: 6
  
paths:
  word_lists: "./data/words"
  stats_file: "~/.hangman/stats.json"

display:
  enable_colors: true
  min_terminal_width: 80
  min_terminal_height: 24

language: "en"
```

---

## 5. API Contracts

### 5.1 Game Engine Interface

```python
class IGameEngine:
    """Interface for the core game engine."""
    
    def start_game(word: str, category: str, difficulty: Difficulty) -> GameState
    def make_guess(letter: str) -> GuessResult
    def get_display_word() -> str
    def is_game_over() -> bool
    def is_win() -> bool
    def get_hangman_stage() -> int
```

### 5.2 Word List Manager Interface

```python
class IWordListManager:
    """Interface for word list management."""
    
    def load_word_lists() -> Dict[str, List[WordEntry]]
    def get_random_word(category: str, difficulty: Difficulty) -> WordEntry
    def get_categories() -> List[str]
    def get_difficulties() -> List[Difficulty]
```

### 5.3 UI Renderer Interface

```python
class IUIRenderer:
    """Interface for terminal UI rendering."""
    
    def clear_screen() -> None
    def display_welcome() -> None
    def display_game_state(state: GameState) -> None
    def display_hangman(stage: int) -> None
    def display_message(msg: str, msg_type: MessageType) -> None
    def get_input(prompt: str) -> str
```

### 5.4 Input Handler Interface

```python
class IInputHandler:
    """Interface for input processing."""
    
    def read_input() -> str
    def validate_input(input: str) -> ValidationResult
    def sanitize_input(input: str) -> str
    def is_quit_command(input: str) -> bool
```

---

## 6. Sequence Diagrams

### 6.1 Game Initialization Sequence

```
User    App       Config    WordMgr    Game      UI
 │       │          │         │         │         │
 │       │          │         │         │         │
 │───►   │          │         │         │         │  Start
 │       │          │         │         │         │
 │       │──────►   │         │         │         │  Load config
 │       │◄───────  │         │         │         │
 │       │          │         │         │         │
 │       │          │──────►  │         │         │  Load words
 │       │          │◄─────── │         │         │
 │       │          │         │         │         │
 │       │          │         │──────►  │         │  Select word
 │       │          │         │◄─────── │         │
 │       │          │         │         │         │
 │       │──────────────────────────►   │         │  Start game
 │       │          │         │         │◄─────── │
 │       │          │         │         │         │
 │       │────────────────────────────────────►   │  Display welcome
 │◄──────│          │         │         │         │
 │       │          │         │         │         │
```

### 6.2 Guess Processing Sequence

```
User    Input     App       Game      UI        Stats
 │       │         │         │         │         │
 │───►   │         │         │         │         │  Enter letter
 │       │────►    │         │         │         │  Read input
 │       │         │         │         │         │
 │       │◄────    │         │         │         │  Validate
 │       │         │         │         │         │
 │       │────────►│         │         │         │  Submit guess
 │       │         │────►    │         │         │  Process guess
 │       │         │◄────    │         │         │  Result
 │       │         │         │         │         │
 │       │         │────────────────►  │         │  Update display
 │       │         │         │         │◄────    │
 │       │         │         │         │         │
 │       │         │─────────────────────────►   │  Update stats
 │◄──────│         │         │         │         │  Show result
 │       │         │         │         │         │
```

### 6.3 Game End Sequence

```
User    App       Game      UI        Stats
 │       │         │         │         │
 │       │         │────►    │         │  Check game over
 │       │         │◄────    │         │  Win/Loss
 │       │         │         │         │
 │       │────────────────►  │         │  Display result
 │       │         │         │◄────    │
 │       │         │         │         │
 │       │─────────────────────────►   │  Save stats
 │       │         │         │         │
 │◄──────│         │         │         │  Play again?
 │       │         │         │         │
 │───►   │         │         │         │  Yes/No
 │       │         │         │         │
 │       │──────►  │         │         │  New game OR Exit
 │       │         │         │         │
```

---

## 7. Technology Stack

### 7.1 Primary Language: **Python 3.9+**

**Justification:**
- **Cross-platform**: Runs on Linux, macOS, Windows without modification
- **Rich standard library**: `curses`, `json`, `datetime`, `pathlib` cover most needs
- **Rapid development**: Clean syntax, minimal boilerplate
- **Testing support**: Built-in `unittest`, `pytest` ecosystem
- **Low barrier**: Easy to maintain and extend
- **Performance adequate**: CLI game has minimal performance requirements

### 7.2 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pyyaml` | ^6.0 | Configuration file parsing |
| `pytest` | ^7.0 | Unit testing framework |
| `pytest-cov` | ^4.0 | Test coverage reporting |
| `black` | ^23.0 | Code formatting |
| `mypy` | ^1.0 | Static type checking |
| `ruff` | ^0.0.250 | Linting |

### 7.3 Development Tools

| Tool | Purpose |
|------|---------|
| `poetry` | Dependency management |
| `pre-commit` | Git hooks |
| `tox` | Multi-environment testing |

---

## 8. Project Structure

```
hangman/
├── pyproject.toml           # Project metadata & dependencies
├── README.md                # User documentation
├── REQUIREMENTS.md          # Requirements specification
├── specs.md                 # Core specifications
├── AGENTS.md                # Agent instructions
│
├── docs/
│   ├── ARCHITECTURE.md      # This document
│   ├── API.md               # API documentation
│   └── DEVELOPMENT.md       # Developer guide
│
├── src/
│   └── hangman/
│       ├── __init__.py
│       ├── __main__.py      # Entry point (python -m hangman)
│       ├── app.py           # Application controller
│       ├── config.py        # Configuration manager
│       ├── game.py          # Game engine (core logic)
│       ├── input_handler.py # Input validation
│       ├── renderer.py      # UI rendering
│       ├── stats.py         # Session statistics
│       └── words.py         # Word list management
│
├── data/
│   └── words/
│       ├── words.json       # Main word list
│       └── custom.json      # User custom words (optional)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_game.py         # Game engine tests
│   ├── test_input.py        # Input handler tests
│   ├── test_renderer.py     # UI renderer tests
│   ├── test_stats.py        # Statistics tests
│   ├── test_words.py        # Word list tests
│   └── test_integration.py  # Integration tests
│
└── config/
    └── default.yaml         # Default configuration
```

---

## 9. Design Patterns

### 9.1 State Pattern
Used in `GameEngine` to manage game states (playing, won, lost).

### 9.2 Strategy Pattern
Word selection strategies for different difficulty levels.

### 9.3 Singleton Pattern
`ConfigurationManager` and `SessionStats` as singletons.

### 9.4 Template Method Pattern
Game loop structure in `ApplicationController`.

---

## 10. Error Handling Strategy

### 10.1 Exception Hierarchy

```
HangmanException (base)
├── ConfigurationError
├── WordListError
│   ├── WordListNotFound
│   └── EmptyWordList
├── GameError
│   ├── InvalidGuess
│   └── GameNotStarted
└── InputError
    ├── InvalidInput
    └── QuitRequested
```

### 10.2 Error Handling Principles

1. **Fail fast**: Validate inputs early
2. **Graceful degradation**: Show helpful messages, never crash
3. **Logging**: Log errors for debugging (optional debug mode)
4. **User-friendly**: Clear, actionable error messages

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Test each module in isolation
- Mock external dependencies
- Target: >80% code coverage

### 11.2 Integration Tests
- Test full game sessions
- Verify component interactions
- Test edge cases (empty word list, invalid config)

### 11.3 Property-Based Tests
- Use `hypothesis` for input validation
- Generate random game scenarios

### 11.4 Manual Testing
- Cross-platform verification
- Terminal size variations
- Accessibility testing

---

## 12. Future Extensibility

### 12.1 Potential Enhancements

| Feature | Architecture Support |
|---------|---------------------|
| Multiplayer | Extract `GameEngine` to service |
| Hints system | Add `IHintProvider` interface |
| Multi-language | `ILocalization` service |
| GUI version | Replace `UIRenderer` implementation |
| Online word lists | Implement `IWordListProvider` |
| Achievements | Extend `SessionStats` |

### 12.2 Plugin Architecture (Future)

```python
class IWordListProvider(ABC):
    """Plugin interface for custom word sources."""
    
    @abstractmethod
    def get_words(self, category: str) -> List[WordEntry]:
        pass
```

---

## 13. Performance Considerations

### 13.1 Targets

| Metric | Target |
|--------|--------|
| Input response | <100ms |
| Word loading | <1s (10k words) |
| Memory usage | <50MB |
| Startup time | <500ms |

### 13.2 Optimization Strategies

- Lazy loading of word lists
- Cache rendered ASCII art
- Minimize I/O operations
- Use generators for large datasets

---

## 14. Security Considerations

### 14.1 Input Sanitization
- Strip whitespace, normalize Unicode
- Reject non-alphabetic characters
- Limit input length

### 14.2 File System Security
- Validate file paths (no directory traversal)
- Read-only access to word lists
- Safe defaults for missing config

### 14.3 Error Messages
- No stack traces to users
- Generic error messages in production
- Detailed logging in debug mode

---

*Document Version: 1.0*
*Created: 2026-03-08*
*Author: System Architect*
