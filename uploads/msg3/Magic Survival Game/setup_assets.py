import os
import wave
import struct
import math

# Setup directories
assets_dir = os.path.join(os.path.dirname(__file__), "assets")
sounds_dir = os.path.join(assets_dir, "sounds")
os.makedirs(assets_dir, exist_ok=True)
os.makedirs(sounds_dir, exist_ok=True)

try:
    from PIL import Image, ImageDraw
    
    # Asset definitions: (name, size, color, description)
    assets = [
        ("wizard", (40, 40), (150, 50, 255), "Wizard character - Purple"),
        ("knight", (40, 40), (100, 100, 100), "Knight character - Gray"),
        ("archer", (40, 40), (50, 200, 50), "Archer character - Green"),
        ("enemy", (30, 30), (200, 50, 50), "Regular enemy - Red"),
        ("boss", (90, 90), (120, 20, 20), "Boss enemy - Dark Red"),
        ("xp", (20, 20), (255, 255, 0), "XP orb - Yellow"),
        ("chest", (30, 30), (200, 150, 50), "Treasure chest - Brown"),
        ("bullet", (8, 8), (255, 255, 255), "Bullet projectile - White"),
        ("orb", (10, 10), (0, 255, 255), "Orb projectile - Cyan"),
        ("legendary", (18, 18), (255, 215, 0), "Legendary item - Gold"),
    ]
    
    print("Creating placeholder PNG files...")
    for name, size, color, desc in assets:
        img = Image.new("RGB", size, color)
        # Add a border or pattern for clarity
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(255, 255, 255))
        filepath = os.path.join(assets_dir, f"{name}.png")
        img.save(filepath)
        print(f"  ✓ Created {name}.png ({desc})")

except ImportError:
    print("PIL/Pillow not found. Creating placeholder images with pygame instead...")
    import pygame
    pygame.init()
    
    assets = [
        ("wizard", (40, 40), (150, 50, 255)),
        ("knight", (40, 40), (100, 100, 100)),
        ("archer", (40, 40), (50, 200, 50)),
        ("enemy", (30, 30), (200, 50, 50)),
        ("boss", (90, 90), (120, 20, 20)),
        ("xp", (20, 20), (255, 255, 0)),
        ("chest", (30, 30), (200, 150, 50)),
        ("bullet", (8, 8), (255, 255, 255)),
        ("orb", (10, 10), (0, 255, 255)),
        ("legendary", (18, 18), (255, 215, 0)),
    ]
    
    for name, size, color in assets:
        surf = pygame.Surface(size)
        surf.fill(color)
        pygame.image.save(surf, os.path.join(assets_dir, f"{name}.png"))
        print(f"  ✓ Created {name}.png")

def create_beep_wav(filepath, frequency=440, duration=0.5, volume=0.3):
    """Create a simple beep WAV file with a sine wave"""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    with wave.open(filepath, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            # Generate sine wave
            sample = int(32767 * volume * math.sin(2 * math.pi * frequency * i / sample_rate))
            # Clamp to 16-bit range
            sample = max(-32768, min(32767, sample))
            wav_file.writeframes(struct.pack('<h', sample))

# Create placeholder WAV files with beep tones
print("\nCreating placeholder audio files...")
sound_files = [
    ("firebreath_burst.wav", 800, 0.2, "Firebreath ability sound"),
    ("level_up_chime.wav", 1000, 0.3, "Level up notification"),
    ("game_over.wav", 300, 0.5, "Game over sound"),
    ("victory.wav", 1200, 0.5, "Victory/win sound"),
    ("boss_music.wav", 500, 2.0, "Boss battle music"),
]

for filename, freq, dur, desc in sound_files:
    filepath = os.path.join(sounds_dir, filename)
    try:
        create_beep_wav(filepath, frequency=freq, duration=dur, volume=0.3)
        print(f"  ✓ Created {filename} ({desc})")
    except Exception as e:
        print(f"  ✗ Error creating {filename}: {e}")


print("\n✓ All placeholder assets created successfully!")
print(f"\nAssets folder: {assets_dir}")
print(f"Sounds folder: {sounds_dir}")
print("\nYou can now replace these placeholder files with your own PNGs and WAV files!")
