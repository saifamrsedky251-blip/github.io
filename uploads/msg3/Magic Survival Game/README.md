# Assets Guide

This folder contains all game assets including character sprites, enemies, projectiles, and sounds.

## Image Assets (PNG files)

Replace these placeholder PNG files with your own graphics:

### Characters (40x40 px recommended)
- **wizard.png** - Wizard character sprite
- **knight.png** - Knight character sprite  
- **archer.png** - Archer character sprite

### Enemies & Bosses
- **enemy.png** - Regular enemy sprite (30x30 px)
- **boss.png** - Boss enemy sprite (90x90 px)

### Items & Effects
- **xp.png** - Experience orb (20x20 px)
- **chest.png** - Treasure chest (30x30 px)
- **bullet.png** - Bullet projectile (8x8 px)
- **orb.png** - Magic orb projectile (10x10 px)
- **legendary.png** - Legendary item (18x18 px)

## Sound Assets

Replace these placeholder audio files in the `sounds/` folder:

### Sound Effects (WAV or MP3)
- **firebreath_burst.wav** - Firebreath ability sound
- **level_up_chime.wav** - Level up notification sound
- **game_over.wav** - Game over sound
- **victory.wav** - Victory/win sound
- **boss_music.mp3** - Boss battle background music

## Installation Instructions

1. Replace placeholder PNG files with your own character/enemy sprites
   - Keep the same dimensions as specified above
   - PNG format with transparency (RGBA) is recommended

2. Replace placeholder audio files with your own sounds
   - WAV format is preferred for sound effects
   - MP3 format for boss music
   - File sizes should be reasonable (< 5MB per file)

3. Run the game - it will automatically load your custom assets!

## Tips

- For best results, use PNG files with transparent backgrounds
- Keep sprite sizes consistent with the original dimensions
- Test your sounds with the game before finalizing
- Backup the placeholder files before replacing them

## Troubleshooting

If assets don't load:
1. Verify file names match exactly (case-sensitive)
2. Check that files are in the correct subdirectory
3. Ensure PNG files are valid and not corrupted
4. For sounds, confirm they're in the `sounds/` subdirectory
