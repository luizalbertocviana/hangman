# Hangman CLI - Component Diagram

## System Context (C4 Level 1)

```mermaid
C4Context
    title System Context Diagram - Hangman CLI Game

    Person(player, "Player", "A person who wants to play Hangman")
    
    System_Boundary(hangman, "Hangman CLI Application") {
        Container(hangman_cli, "Hangman CLI", "Python", "Command-line Hangman game")
    }

    System_Ext(terminal, "Terminal/Shell", "Provides stdin/stdout interface")
    System_Ext(word_files, "Word List Files", "JSON/YAML", "External word data")
    System_Ext(stats_file, "Stats File", "JSON", "Session statistics storage")

    Rel(player, terminal, "Uses", "keyboard/display")
    Rel(terminal, hangman_cli, "Runs")
    Rel(hangman_cli, word_files, "Reads", "JSON")
    Rel(hangman_cli, stats_file, "Read/Writes", "JSON")

    UpdateRelStyle(player, terminal, $offsetY="-30")
    UpdateRelStyle(terminal, hangman_cli, $offsetX="40")
    UpdateRelStyle(hangman_cli, word_files, $offsetY="40")
    UpdateRelStyle(hangman_cli, stats_file, $offsetY="-40")
```

## Container Diagram (C4 Level 2)

```mermaid
C4Container
    title Container Diagram - Hangman CLI Application

    Person(player, "Player", "A person who wants to play Hangman")
    
    System_Boundary(hangman, "Hangman CLI Application") {
        Container(main, "Main Entry Point", "Python", "Application bootstrap and signal handling")
        Container(app, "Application Controller", "Python", "Game session orchestration")
        Container(config, "Configuration Manager", "Python", "Settings management")
        Container(game, "Game Engine", "Python", "Core game logic and state")
        Container(words, "Word List Manager", "Python", "Word data access and filtering")
        Container(ui, "UI Renderer", "Python", "Terminal display and ASCII art")
        Container(input, "Input Handler", "Python", "User input validation")
        Container(stats, "Session Statistics", "Python", "Stats tracking and persistence")
    }

    System_Ext(word_files, "Word List Files", "JSON")
    System_Ext(config_file, "Config File", "YAML")
    System_Ext(stats_file, "Stats File", "JSON")

    Rel(player, ui, "Interacts with")
    Rel(ui, input, "Uses")
    Rel(input, app, "Provides validated input")
    Rel(app, main, "Controlled by")
    Rel(app, game, "Orchestrates")
    Rel(app, stats, "Updates")
    Rel(game, words, "Requests words from")
    Rel(words, word_files, "Loads from")
    Rel(config, config_file, "Loads from")
    Rel(stats, stats_file, "Persists to")
    Rel(app, config, "Reads configuration")
    Rel(ui, config, "Reads display settings")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

## Component Diagram - Game Engine

```mermaid
C4Component
    title Component Diagram - Game Engine

    Boundary(game_boundary, "Game Engine Module") {
        Component(game_state, "GameState", "Class", "Holds current game state")
        Component(guess_eval, "GuessEvaluator", "Class", "Validates and processes guesses")
        Component(win_checker, "WinConditionChecker", "Class", "Detects win/loss conditions")
        Component(hangman_state, "HangmanState", "Class", "Tracks hangman drawing stage")
    }

    Component(word_mgr, "Word List Manager", "Module", "Provides words")
    Component(ui_render, "UI Renderer", "Module", "Displays state")

    Rel(guess_eval, game_state, "Updates")
    Rel(guess_eval, win_checker, "Notifies")
    Rel(win_checker, hangman_state, "Checks")
    Rel(game_state, word_mgr, "Requests word from")
    Rel(game_state, ui_render, "Sends state to")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Deployment Diagram

```mermaid
graph TD
    subgraph "User's Machine"
        subgraph "Terminal Environment"
            Shell[Terminal/Shell]
            Hangman[Hangman CLI Process]
        end
        
        subgraph "File System"
            WordFiles[./data/words/]
            ConfigFile[~/.hangman/config.yaml]
            StatsFile[~/.hangman/stats.json]
        end
    end

    Shell -->|executes| Hangman
    Hangman -->|reads| WordFiles
    Hangman -->|reads| ConfigFile
    Hangman -->|reads/writes| StatsFile

    style Hangman fill:#4CAF50,color:white
    style Shell fill:#2196F3,color:white
```

---

*Created: 2026-03-08*
*Author: System Architect*
