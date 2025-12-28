# Lua Scripts Archive

This directory contains custom Lua scripts from archived OTClient Tibia bot projects.

## Overview

These scripts are custom bot scripts for OTCv8 (Open Tibia Client version 8), a modified Tibia game client that supports bot automation through Lua scripting.

## Original Sources

The scripts were consolidated from the following repositories before they were archived:

- **fesio/otcTibia** - https://github.com/fesio/otcTibia
- **fesio/otcv8-dev** - https://github.com/fesio/otcv8-dev

## Directory Structure

```
scripts/lua/
├── otc/                    # Scripts from fesio/otcTibia
│   └── _Loader.lua        # Main loader script with targeting, PVP, and equipment macros
└── otcv8/                  # Scripts from fesio/otcv8-dev
    ├── _Loader.lua        # Same main loader script (shared between repos)
    ├── SuperDash.lua      # Dash mechanics and damage analyzer
    ├── magebomb.lua       # Team bombing coordin ation and auto-party system
    ├── follow_and_party.lua # Jewelry auto-equip, mana training, and healing
    ├── init.lua           # OTCv8 initialization and configuration
    └── test.lua           # Test framework script
```

## Script Descriptions

### otc/_Loader.lua
Main bot loader that includes:
- Smart targeting system (targets lowest HP monster within range)
- PVP spell macros with range and mana cost management
- Auto energy ring equipment based on HP thresholds
- Paladin spell handling with momentum effect detection
- Food consumption automation

### otcv8/SuperDash.lua
Advanced movement and combat features:
- Super dash mechanics triggered by WASD/arrow keys
- Pathfinding debugger
- Damage analyzer tracking different damage types (Physical, Fire, Ice, Energy, etc.)
- Life steal detection
- Color-coded damage statistics with percentages

### otcv8/magebomb.lua
Team coordination for mage bombing strategies:
- Leader/follower synchronization system
- Position mirroring and auto-walk to leader
- Shared attack targeting via BotServer
- Item usage coordination (switches, levers, runes)
- Auto-party invitation and management
- Auto-follow functionality with multi-floor support

### otcv8/follow_and_party.lua
Jewelry management and healing:
- Auto-equip rings and amulets based on HP%/MP% thresholds
- Smart jewelery swapping (returns to default items when safe)
- Mana training mode
- Health and mana potion automation
- Multiple item configurations (potions, runes)
- Support for various amulets (SSA, Plasma, Shockwave, Glacier, Magma, etc.)
- Rune spamming system with configurable IDs

### otcv8/init.lua
OTCv8 client initialization:
- Application configuration (name, version, layout)
- Service URLs (updater, crash reporter, feedback)
- Server list configuration
- Module loading sequence (libraries → client → game → mods)
- Auto-updater integration

### otcv8/test.lua
Simple test framework:
- Window maximization test
- Screenshot functionality
- Test execution framework

## How to Use

These scripts are designed to be loaded within the OTCv8 client:

1. **Install OTCv8** - Download and install the OTCv8 client
2. **Place scripts** - Copy the relevant `.lua` files to your OTCv8 bot scripts directory
3. **Load via UI** - Use the OTCv8 bot interface to load and configure the scripts
4. **Configure macros** - Adjust HP/MP thresholds, spell names, and item IDs as needed

## Important Notes

- **Historical Archive**: These scripts are preserved for reference only
- **No Active Development**: These are backups from archived projects
- **Compatibility**: Scripts are designed for OTCv8 client (may not work with other clients)
- **Use at Own Risk**: Bot automation may violate game terms of service

## Migration Information

- **Migration Date**: December 28, 2024
- **Reason**: Consolidation before archiving source repositories
- **Original Repositories**: Now archived/deleted to prevent data loss

## License

These scripts were created for personal use. Original licensing terms from the source repositories apply (if any).

## Technical Details

### Language
- Lua 5.1+ (OTCv8 uses embedded Lua)

### Dependencies
- OTCv8 client
- OTCv8 bot module
- vBot framework (referenced in _Loader.lua)

### Key Features Used
- OTCv8 game API (`g_game`, `g_map`, `g_ui`, etc.)
- Event hooks (`onTextMessage`, `onCreatureAppear`, `onAddThing`, etc.)
- Macro system for automation
- UI widget creation
- BotServer for multi-client communication

---

**Note**: This is an archival copy for preservation purposes. For active OTCv8 development, please refer to the current OTCv8 community resources.
