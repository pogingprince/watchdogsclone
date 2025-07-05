import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Urban Game"
DARK_GREY = (50, 50, 50)
LIGHT_BLUE = (100, 100, 255)
OBJECT_COLOR = (120, 120, 120) # Slightly different grey for environment objects
CAMERA_COLOR = (200, 200, 0) # Yellow
HACKED_CAMERA_COLOR = (0, 255, 0) # Green
PLAYER_NORMAL_COLOR_PLACEHOLDER = LIGHT_BLUE # Will be set in Player __init__
PLAYER_DETECTED_COLOR = (255, 0, 0) # Red
ZONE_NORMAL_COLOR = (100, 0, 0, 150) # Dark Red, semi-transparent for later
ZONE_DETECTED_COLOR = (180, 0, 0, 200) # Brighter Dark Red, semi-transparent for later
# For now, using solid colors for zones as per plan
SOLID_ZONE_NORMAL_COLOR = (100, 0, 0)
SOLID_ZONE_DETECTED_COLOR = (180, 0, 0)
PLAYER_SPEED = 1 # Further reduced player speed from 3 to 1 (original was 5)

# UI Settings
UI_FONT_SIZE = 28
UI_TEXT_COLOR = (230, 230, 230) # Light grey/white
UI_PANEL_COLOR = (30, 30, 30) # Dark background for UI
UI_FONT = None # Will be initialized after pygame.init()

# Game Mechanics Settings
BULLET_COLOR = (255, 255, 0) # Yellow - Retained
BULLET_SPEED = 10
BULLET_SIZE = (6, 8) # Changed from (5,5) for better visibility and slight elongation
EXPLOSION_INITIAL_COLOR = (255, 255, 0) # Yellow - Retained
EXPLOSION_MIDDLE_COLOR = (255, 165, 0) # Orange - Retained
EXPLOSION_FINAL_COLOR = (255, 0, 0) # Red - Retained
EXPLOSION_DURATION = 35 # Changed from 30 for slightly longer persistence
EXPLOSION_INITIAL_RADIUS = 5
EXPLOSION_MAX_RADIUS = 60 # Changed from 50 for a larger impact area

# World dimensions
WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200

# Camera class
class Camera:
    def __init__(self, world_width, world_height):
        self.camera_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.world_width = world_width
        self.world_height = world_height

    def update(self, target_rect):
        # Target camera position to center the target_rect
        target_x = target_rect.centerx - SCREEN_WIDTH // 2
        target_y = target_rect.centery - SCREEN_HEIGHT // 2

        # Clamp camera position to world boundaries
        # Camera's top-left x should not be less than 0
        self.camera_rect.x = max(0, target_x)
        # Camera's top-left y should not be less than 0
        self.camera_rect.y = max(0, target_y)

        # Camera's right edge should not exceed world_width
        if self.camera_rect.right > self.world_width:
            self.camera_rect.right = self.world_width
        # Camera's bottom edge should not exceed world_height
        if self.camera_rect.bottom > self.world_height:
            self.camera_rect.bottom = self.world_height

        # Handle cases where world is smaller than screen
        if self.world_width < SCREEN_WIDTH:
            self.camera_rect.x = (self.world_width - SCREEN_WIDTH) // 2
        if self.world_height < SCREEN_HEIGHT:
            self.camera_rect.y = (self.world_height - SCREEN_HEIGHT) // 2


    def apply(self, entity_rect):
        # Return a new rect offset by the camera's position
        return entity_rect.move(-self.camera_rect.x, -self.camera_rect.y)

# EnvironmentObject class
class EnvironmentObject:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surface, display_rect):
        pygame.draw.rect(surface, self.color, display_rect)

# CameraObject class
class CameraObject:
    def __init__(self, x, y, width, height, color, hacked_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hacked_color = hacked_color
        self.is_hacked = False

    def draw(self, surface, display_rect):
        current_color = self.hacked_color if self.is_hacked else self.color
        pygame.draw.rect(surface, current_color, display_rect)

    def hack(self):
        self.is_hacked = not self.is_hacked # Toggle state

# SecurityZone class
class SecurityZone:
    def __init__(self, x, y, width, height, color, detected_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.detected_color = detected_color
        self.player_is_inside = False

    def draw(self, surface, display_rect):
        current_color = self.detected_color if self.player_is_inside else self.color
        # For now, drawing solid rects. Transparency would need a separate surface.
        pygame.draw.rect(surface, current_color, display_rect)

    def update(self, player_rect):
        self.player_is_inside = self.rect.colliderect(player_rect)

# Bullet class
class Bullet:
    def __init__(self, x, y, direction_x, direction_y, speed, color):
        self.rect = pygame.Rect(x, y, BULLET_SIZE[0], BULLET_SIZE[1])
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = speed
        self.color = color

    def update(self):
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed

    def draw(self, surface, display_rect):
        pygame.draw.rect(surface, self.color, display_rect)

# Explosion class
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.current_radius = EXPLOSION_INITIAL_RADIUS
        self.life = EXPLOSION_DURATION
        # Initial rect for camera.apply, will be updated
        self.rect = pygame.Rect(
            x - self.current_radius,
            y - self.current_radius,
            2 * self.current_radius,
            2 * self.current_radius
        )

    def update(self):
        self.life -= 1
        if self.life <= 0:
            return

        progress = (EXPLOSION_DURATION - self.life) / EXPLOSION_DURATION
        self.current_radius = EXPLOSION_INITIAL_RADIUS + progress * (EXPLOSION_MAX_RADIUS - EXPLOSION_INITIAL_RADIUS)

        # Update self.rect for camera application
        self.rect.width = 2 * self.current_radius
        self.rect.height = 2 * self.current_radius
        self.rect.centerx = self.x
        self.rect.centery = self.y


    def draw(self, surface, display_rect):
        # display_rect is camera.apply(self.rect)
        # We need to draw the circle at the center of this camera-adjusted rect

        color = EXPLOSION_FINAL_COLOR
        if self.life > (2/3 * EXPLOSION_DURATION):
            color = EXPLOSION_INITIAL_COLOR
        elif self.life > (1/3 * EXPLOSION_DURATION):
            color = EXPLOSION_MIDDLE_COLOR

        # Ensure radius is an integer for drawing
        draw_radius = int(self.current_radius)
        if draw_radius > 0: # Only draw if radius is positive
             pygame.draw.circle(surface, color, display_rect.center, draw_radius)


# Weapon class
class Weapon:
    def __init__(self, name, weapon_type, ammo, max_ammo, clip_size, current_clip_ammo):
        self.name = name
        self.weapon_type = weapon_type
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.clip_size = clip_size
        self.current_clip_ammo = current_clip_ammo

# Player class
class Player:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.normal_color = LIGHT_BLUE # Original player color
        self.detected_color = PLAYER_DETECTED_COLOR
        self.is_detected = False
        # Player starts in the middle of the world
        self.rect = pygame.Rect(
            (WORLD_WIDTH - self.width) // 2,
            (WORLD_HEIGHT - self.height) // 2,
            self.width,
            self.height
        )
        self.speed = PLAYER_SPEED
        self.inventory = []
        self.show_arsenal = False # Attribute to control arsenal display
        self.selected_weapon_index = 0
        self.current_weapon = None # Will be set after inventory initialization
        self.bullets = [] # List to store active bullets
        self.explosions = [] # List to store active explosions
        self._initialize_starting_inventory()
        # Ensure current_weapon is set if inventory is not empty
        if self.inventory:
            self.current_weapon = self.inventory[self.selected_weapon_index]


    def _initialize_starting_inventory(self):
        # Create "1911" pistol
        pistol_1911 = Weapon(
            name="1911",
            weapon_type="firearm",
            ammo=30,
            max_ammo=90,
            clip_size=10,
            current_clip_ammo=10
        )
        self.inventory.append(pistol_1911)

        # Create IEDs (one object with ammo=3)
        ied_explosive = Weapon(
            name="IED",
            weapon_type="explosive",
            ammo=3,
            max_ammo=3,
            clip_size=None, # IEDs don't have clips
            current_clip_ammo=None # No clip, so no ammo in clip
        )
        self.inventory.append(ied_explosive)

    def select_weapon(self, index):
        if 0 <= index < len(self.inventory):
            self.selected_weapon_index = index
            self.current_weapon = self.inventory[self.selected_weapon_index]
        # else: print(f"Invalid weapon index: {index}") # Optional: for debugging

    def fire_weapon(self):
        if self.current_weapon and self.current_weapon.name == "1911":
            if self.current_weapon.current_clip_ammo > 0:
                self.current_weapon.current_clip_ammo -= 1

                # For now, bullet shoots upwards from player center
                # A more sophisticated approach would consider player orientation
                bullet_start_x = self.rect.centerx - BULLET_SIZE[0] // 2
                bullet_start_y = self.rect.top # Fires from the top-middle of the player

                new_bullet = Bullet(
                    bullet_start_x,
                    bullet_start_y,
                    0,  # direction_x (0 for straight up)
                    -1, # direction_y (-1 for up)
                    BULLET_SPEED,
                    BULLET_COLOR
                )
                self.bullets.append(new_bullet)
            # else: print("1911 empty clip!") # For debugging
        elif self.current_weapon and self.current_weapon.name == "IED":
            if self.current_weapon.ammo > 0:
                self.current_weapon.ammo -= 1
                explosion_x = self.rect.centerx
                explosion_y = self.rect.centery
                new_explosion = Explosion(explosion_x, explosion_y)
                self.explosions.append(new_explosion)
                # print(f"Deployed IED. Remaining: {self.current_weapon.ammo}") # For debugging
            # else: print("No IEDs left!") # For debugging
        # else: print("No weapon selected or unknown weapon.") # For debugging

    def reload_weapon(self):
        if self.current_weapon and self.current_weapon.weapon_type == "firearm":
            if self.current_weapon.clip_size is None: # Not a clippable weapon (e.g. some shotguns)
                # print(f"{self.current_weapon.name} does not use clips.")
                return

            if self.current_weapon.current_clip_ammo < self.current_weapon.clip_size:
                if self.current_weapon.ammo > 0:
                    ammo_needed = self.current_weapon.clip_size - self.current_weapon.current_clip_ammo
                    ammo_to_transfer = min(ammo_needed, self.current_weapon.ammo)

                    self.current_weapon.current_clip_ammo += ammo_to_transfer
                    self.current_weapon.ammo -= ammo_to_transfer
                    # print(f"Reloaded {self.current_weapon.name}. Clip: {self.current_weapon.current_clip_ammo}/{self.current_weapon.ammo}") # For debugging
                # else:
                    # print("No reserve ammo to reload!") # For debugging
            # else:
                # print(f"{self.current_weapon.name} clip is full.") # For debugging
        # else:
            # print("No firearm selected to reload.") # For debugging


    def draw_arsenal(self, surface):
        if not self.show_arsenal:
            return

        panel_x, panel_y = 10, 10
        panel_width = 250
        # Dynamically adjust panel height based on number of items, or use a fixed height
        num_items = len(self.inventory)
        panel_height = 30 + num_items * 30 # Base height + per item height

        # Draw background panel
        pygame.draw.rect(surface, UI_PANEL_COLOR, (panel_x, panel_y, panel_width, panel_height))

        text_y_offset = 15 # Initial y offset from panel's top
        line_height = 30   # Space between lines of text

        for weapon in self.inventory:
            display_text = ""
            if weapon.weapon_type == "firearm":
                display_text = f"{weapon.name}: {weapon.current_clip_ammo}/{weapon.ammo}"
            elif weapon.weapon_type == "explosive":
                display_text = f"{weapon.name}: {weapon.ammo}"
            else:
                display_text = f"{weapon.name}: N/A" # Fallback for other types

            text_surface = UI_FONT.render(display_text, True, UI_TEXT_COLOR)
            surface.blit(text_surface, (panel_x + 10, panel_y + text_y_offset))
            text_y_offset += line_height

    def draw_current_weapon_indicator(self, surface):
        if self.current_weapon:
            display_text = f"Selected: {self.current_weapon.name}"
            text_surface = UI_FONT.render(display_text, True, UI_TEXT_COLOR)
            # Position at bottom-center of the screen
            text_x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
            text_y = SCREEN_HEIGHT - 40 # 40 pixels from the bottom
            surface.blit(text_surface, (text_x, text_y))

    def draw(self, surface, display_rect): # display_rect is the camera-adjusted rect
        current_color = self.detected_color if self.is_detected else self.normal_color
        pygame.draw.rect(surface, current_color, display_rect)

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if pressed_keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if pressed_keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if pressed_keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Keep player within world boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WORLD_WIDTH:
            self.rect.right = WORLD_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WORLD_HEIGHT:
            self.rect.bottom = WORLD_HEIGHT

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

# Create player instance
player = Player()
# Create camera instance
camera = Camera(WORLD_WIDTH, WORLD_HEIGHT)

# Initialize Font (must be done after pygame.init())
UI_FONT = pygame.font.Font(None, UI_FONT_SIZE)

# Create environment objects
environment_objects = [
    EnvironmentObject(100, 100, 200, 100, OBJECT_COLOR),
    EnvironmentObject(400, 300, 100, 150, OBJECT_COLOR),
    EnvironmentObject(700, 50, 150, 200, OBJECT_COLOR),
    EnvironmentObject(1000, 400, 200, 120, OBJECT_COLOR),
    EnvironmentObject(50, 500, 300, 50, OBJECT_COLOR), # A wide, short object
    EnvironmentObject(1300, 100, 50, 400, OBJECT_COLOR) # A tall, thin object
]

# Create CameraObject instances
camera_objects = [
    CameraObject(200, 50, 20, 20, CAMERA_COLOR, HACKED_CAMERA_COLOR),
    CameraObject(500, 250, 20, 20, CAMERA_COLOR, HACKED_CAMERA_COLOR),
    CameraObject(800, 400, 25, 25, CAMERA_COLOR, HACKED_CAMERA_COLOR)
]

# Create SecurityZone instances
security_zones = [
    SecurityZone(300, 200, 150, 150, SOLID_ZONE_NORMAL_COLOR, SOLID_ZONE_DETECTED_COLOR),
    SecurityZone(700, 500, 100, 200, SOLID_ZONE_NORMAL_COLOR, SOLID_ZONE_DETECTED_COLOR)
]

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                for cam_obj in camera_objects:
                    if player.rect.colliderect(cam_obj.rect):
                        cam_obj.hack()
            elif event.key == pygame.K_l: # Toggle arsenal display
                player.show_arsenal = not player.show_arsenal
            elif event.key == pygame.K_1:
                player.select_weapon(0)
            elif event.key == pygame.K_2:
                player.select_weapon(1)
            elif event.key == pygame.K_SPACE: # Fire weapon
                player.fire_weapon()
            elif event.key == pygame.K_r: # Reload weapon
                player.reload_weapon()
            # Add more keys (K_3, K_4, etc.) if more weapons can be carried

    # Get pressed keys
    pressed_keys = pygame.key.get_pressed()

    # --- Game Logic Updates ---
    # Update player
    player.update(pressed_keys)

    # Update camera
    camera.update(player.rect)

    # Update bullets
    for bullet in player.bullets:
        bullet.update()
    # Remove bullets that are off-screen (world boundaries)
    world_bounds_rect = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
    player.bullets = [b for b in player.bullets if world_bounds_rect.colliderect(b.rect)]

    # Update explosions
    for explosion in player.explosions:
        explosion.update()
    # Remove dead explosions
    player.explosions = [e for e in player.explosions if e.life > 0]


    # Update security zones and player detection status
    player.is_detected = False # Reset detection status
    for zone in security_zones:
        zone.update(player.rect)
        if zone.player_is_inside:
            player.is_detected = True # Set to true if any zone detects player

    # --- Rendering ---
    # Fill the screen
    screen.fill(DARK_GREY)

    # Draw security zones (drawn first, so they appear as ground markings)
    for zone in security_zones:
        zone.draw(screen, camera.apply(zone.rect))

    # Draw environment objects
    for obj in environment_objects:
        obj.draw(screen, camera.apply(obj.rect))

    # Draw camera objects
    for cam_obj in camera_objects:
        cam_obj.draw(screen, camera.apply(cam_obj.rect))

    # Draw bullets and explosions (explosions drawn first, so they are "under" bullets if overlap)
    for explosion in player.explosions:
        explosion.draw(screen, camera.apply(explosion.rect))
    for bullet in player.bullets:
        bullet.draw(screen, camera.apply(bullet.rect))

    # Draw player (using camera.apply to get screen coordinates)
    player.draw(screen, camera.apply(player.rect))

    # Draw Arsenal UI (on top of everything else)
    player.draw_arsenal(screen)

    # Draw Current Weapon Indicator
    player.draw_current_weapon_indicator(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
