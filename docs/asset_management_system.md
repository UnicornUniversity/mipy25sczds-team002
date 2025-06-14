# Asset Management System - Deadlock Game

## Přehled

Asset Management System poskytuje centralizovanou správu všech herních art assetů s důrazem na vizuální konzistenci a optimalizaci výkonu.

## Hlavní komponenty

### 1. Sprite Loader (`src/utils/sprite_loader.py`)

Centrální systém pro načítání a správu spritů:

```python
from utils.sprite_loader import get_sprite, load_all_assets, get_asset_info

# Načtení všech assetů
load_all_assets()

# Získání konkrétního spritu
player_sprite = get_sprite('player_idle')
zombie_sprite = get_sprite('zombie_basic_1')
grass_tile = get_sprite('tile_grass')

# Informace o načtených assetech
info = get_asset_info()
print(f"Načteno {info['total_sprites']} spritů")
```

#### Funkce:
- **Automatické načítání spritesheetů** - Extrahuje jednotlivé sprity ze spritesheetů
- **Fallback systém** - Vytváří barevné náhrady když sprite neexistuje
- **Optimalizace výkonu** - Optimalizuje pygame surface pro rychlejší rendering
- **Škálování a cache** - Podporuje škálované verze spritů s cache systémem

### 2. Rozšířené konstanty (`src/utils/constants.py`)

Definuje standardy pro vizuální konzistenci:

#### Barevná paleta:
```python
COLOR_PALETTE = {
    'player_primary': (60, 120, 60),      # Dark green
    'zombie_basic': (150, 50, 50),        # Dark red
    'tile_grass': (50, 120, 50),          # Grass green
    'ui_accent': (255, 200, 50),          # Golden yellow
    # ...další barvy
}
```

#### Asset kategorie:
```python
ASSET_CATEGORIES = {
    'characters': ['player', 'zombie'],
    'tiles': ['grass', 'dirt', 'stone', 'wall', 'tree', 'building'],
    'weapons': ['pistol', 'rifle', 'shotgun'],
    'items': ['health', 'ammo', 'key'],
    'effects': ['muzzle_flash', 'blood', 'explosion'],
    'ui': ['button', 'bar', 'icon']
}
```

### 3. Integrace v herních entitách

#### Player (`src/entities/player.py`)
- Používá sprite animace místo jednoduchých kruhů
- Animace chůze s 4 frame cyklem
- Transparentní efekt při pohybu na objektech
- Fallback na kruhy pokud sprity nejsou dostupné

#### Zombie (`src/entities/zombies.py`)
- Sprite animace s 2 frame cyklem
- Pomalejší animace než hráč
- Transparentní efekt na objektech
- Fallback systém

#### MapGenerator (`src/game/map_generator.py`)
- Používá tile sprity místo barev
- Mapování tile typů na konkrétní sprity
- Automatický fallback na barevné čtverce

## Aktuální stav assetů

### Načtené spritesheety:
- **spritesheet_characters.png** - Postavy (hráč, zombies)
- **spritesheet_tiles.png** - Prostředí (tráva, zdi, objekty)

### Extrahované sprity:
- **Player**: player_idle, player_walk_1, player_walk_2, player_walk_3
- **Zombies**: zombie_basic_1, zombie_basic_2, zombie_runner_1, zombie_runner_2, zombie_tank_1, zombie_tank_2
- **Tiles**: tile_grass, tile_dirt, tile_stone, tile_wall_brick, tile_tree, tile_building_wall, atd.

**Celkem načteno: 26 spritů**

## Debug informace

Stisknutím **F1** v gameplay módu se zobrazí debug informace včetně:
- Počet načtených spritů
- Počet spritesheetů
- Stav asset management systému
- Vizuální konzistence status
- Performance optimalizace status

## Optimalizace výkonu

### Implementované optimalizace:
1. **Surface optimization** - Všechny sprity se optimalizují pro rychlejší blitting
2. **Sprite caching** - Škálované verze se cache-ují
3. **Lazy loading** - Assety se načítají pouze při prvním použití
4. **Fallback system** - Minimalizuje chyby při chybějících assetech

### Nastavení výkonu:
```python
SPRITE_CACHE_SIZE = 256           # Maximální počet cache-ovaných variant
ENABLE_SPRITE_OPTIMIZATION = True # Povolení optimalizace surface
TEXTURE_FILTER = 'nearest'        # Filtrování pro pixel art
```

## Vizuální konzistence

### Standardy:
- **Pixel art styl** - Nearest neighbor filtering
- **Konzistentní barevná paleta** - Definovaná v COLOR_PALETTE
- **Standardní velikosti** - TILE_SIZE=32, PLAYER_SIZE=32, ENEMY_SIZE=24
- **Animační standardy** - Definované rychlosti a frame counts

### Pravidla pro nové assety:
1. Dodržovat velikosti definované v konstantách
2. Používat barvy z COLOR_PALETTE
3. Zachovat pixel art styl
4. Všechny sprity musí mít fallback řešení

## Použití v kódu

### Základní použití:
```python
from utils.sprite_loader import get_sprite

# V render metodě entity
sprite = get_sprite('player_idle')
if sprite:
    screen.blit(sprite, (x, y))
else:
    # Fallback drawing
    pygame.draw.circle(screen, color, (x, y), radius)
```

### Animace:
```python
# V update metodě
if self.is_moving:
    frame_index = int(self.animation_time / frame_duration) % 4
    sprite = get_sprite(f'player_walk_{frame_index}')
else:
    sprite = get_sprite('player_idle')
```

## Rozšíření systému

### Přidání nových spritů:
1. Umístit spritesheet do `assets/images/spritesheets/`
2. Upravit `_extract_sprites_from_sheet()` v AssetManager
3. Definovat názvy spritů a jejich pozice
4. Přidat fallback barvy do konstant

### Nové asset kategorie:
1. Přidat do `ASSET_CATEGORIES` v constants.py
2. Vytvořit odpovídající barvy v `COLOR_PALETTE`
3. Implementovat načítání v `_load_individual_sprites()`

## Výhody systému

✅ **Centralizovaná správa** - Všechny assety na jednom místě
✅ **Vizuální konzistence** - Standardizované barvy a velikosti  
✅ **Performance optimalizace** - Optimalizované surface a caching
✅ **Robustnost** - Fallback systém předchází crashům
✅ **Rozšiřitelnost** - Snadné přidávání nových assetů
✅ **Debug support** - Informace o stavu systému
✅ **Backward compatibility** - Zachovává funkčnost při chybějících assetech 