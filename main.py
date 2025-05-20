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
PLAYER_SPEED = 5

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

    # Get pressed keys
    pressed_keys = pygame.key.get_pressed()

    # Update player
    player.update(pressed_keys)

    # Update camera
    camera.update(player.rect)

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

    # Draw player (using camera.apply to get screen coordinates)
    player.draw(screen, camera.apply(player.rect))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
