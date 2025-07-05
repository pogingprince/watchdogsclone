// Screen dimensions
const SCREEN_WIDTH = 800;
const SCREEN_HEIGHT = 600;
const SCREEN_TITLE = "Urban Game"; // Not directly used by p5, but good for reference

// Colors (matching Python version)
let DARK_GREY;
let LIGHT_BLUE;
let OBJECT_COLOR;
let CAMERA_COLOR;
let HACKED_CAMERA_COLOR;
let PLAYER_DETECTED_COLOR;
let ZONE_NORMAL_COLOR_RGBA; // p5.js uses fill(r,g,b,a) where a is 0-255
let ZONE_DETECTED_COLOR_RGBA;

// Player settings
const PLAYER_SPEED = 5; // Keep consistent with Pygame version

// World dimensions
const WORLD_WIDTH = 1600;
const WORLD_HEIGHT = 1200;

// Game entities - to be populated
let player;
let environmentObjects = [];
let cameraObjects = [];
let securityZones = [];

// Camera object (global for now, might be part of a game manager later)
let gameCamera;

// p5.js setup function - runs once at the beginning
function setup() {
    createCanvas(SCREEN_WIDTH, SCREEN_HEIGHT);

    // Initialize colors
    DARK_GREY = color(50, 50, 50);
    LIGHT_BLUE = color(100, 100, 255);
    OBJECT_COLOR = color(120, 120, 120);
    CAMERA_COLOR = color(200, 200, 0);
    HACKED_CAMERA_COLOR = color(0, 255, 0);
    PLAYER_DETECTED_COLOR = color(255, 0, 0);
    // Pygame ZONE_NORMAL_COLOR = (100, 0, 0, 150)
    // Pygame ZONE_DETECTED_COLOR = (180, 0, 0, 200)
    // p5.js alpha is 0-255, Pygame's Surface alpha was also 0-255 for fill.
    ZONE_NORMAL_COLOR_RGBA = color(100, 0, 0, 150);
    ZONE_DETECTED_COLOR_RGBA = color(180, 0, 0, 200);

    // Initialize Camera
    gameCamera = new Camera(WORLD_WIDTH, WORLD_HEIGHT);

    // Initialize Camera
    gameCamera = new Camera(WORLD_WIDTH, WORLD_HEIGHT);

    // Initialize Player
    player = new Player();

    // Initialize EnvironmentObjects
    environmentObjects.push(new EnvironmentObject(100, 100, 200, 100));
    environmentObjects.push(new EnvironmentObject(400, 300, 100, 150));
    environmentObjects.push(new EnvironmentObject(700, 50, 150, 200));
    environmentObjects.push(new EnvironmentObject(1000, 400, 200, 120));
    environmentObjects.push(new EnvironmentObject(50, 500, 300, 50));
    environmentObjects.push(new EnvironmentObject(1300, 100, 50, 400));

    // Initialize CameraObjects
    cameraObjects.push(new CameraObject(200, 50, 20, 20));
    cameraObjects.push(new CameraObject(500, 250, 20, 20));
    cameraObjects.push(new CameraObject(800, 400, 25, 25));

    // Initialize SecurityZones
    securityZones.push(new SecurityZone(300, 200, 150, 150));
    securityZones.push(new SecurityZone(700, 500, 100, 200));
}

// p5.js draw function - runs repeatedly in a loop
function draw() {
    background(DARK_GREY);

    // --- Input and Updates ---
    player.handleInput();
    player.update();

    gameCamera.update(player.x + player.w / 2, player.y + player.h / 2); // Pass player center

    player.isDetected = false; // Reset detection status
    for (let zone of securityZones) {
        zone.update(player); // Pass the player object for collision check
        if (zone.playerIsInside) {
            player.isDetected = true;
        }
    }

    // --- Rendering ---
    push(); // Start a new drawing state for camera view
    gameCamera.apply();

    // Draw world boundary for reference (optional)
    // stroke(255); noFill(); rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT); noStroke();

    // Draw security zones (first, so they are behind other objects)
    for (let zone of securityZones) {
        zone.draw();
    }

    // Draw environment objects
    for (let obj of environmentObjects) {
        obj.draw();
    }

    // Draw camera objects
    for (let camObj of cameraObjects) {
        camObj.draw();
    }

    // Draw player
    player.draw();

    pop(); // Restore original drawing state

    // UI elements or other fixed screen elements can be drawn here (after pop)
}

// --- Entity Classes ---

// Player class
class Player {
    constructor() {
        this.w = 30;
        this.h = 30;
        this.x = (WORLD_WIDTH - this.w) / 2;
        this.y = (WORLD_HEIGHT - this.h) / 2;
        this.speed = PLAYER_SPEED;
        this.isDetected = false;
        this.normalColor = LIGHT_BLUE; // p5.js color object
        this.detectedColor = PLAYER_DETECTED_COLOR; // p5.js color object
    }

    handleInput() {
        if (keyIsDown(LEFT_ARROW)) {
            this.x -= this.speed;
        }
        if (keyIsDown(RIGHT_ARROW)) {
            this.x += this.speed;
        }
        if (keyIsDown(UP_ARROW)) {
            this.y -= this.speed;
        }
        if (keyIsDown(DOWN_ARROW)) {
            this.y += this.speed;
        }
    }

    update() {
        // Keep player within world boundaries
        this.x = constrain(this.x, 0, WORLD_WIDTH - this.w);
        this.y = constrain(this.y, 0, WORLD_HEIGHT - this.h);
    }

    draw() {
        fill(this.isDetected ? this.detectedColor : this.normalColor);
        noStroke();
        rect(this.x, this.y, this.w, this.h);
    }

    // Helper for collision detection (AABB)
    collidesWith(other) {
        return (
            this.x < other.x + other.w &&
            this.x + this.w > other.x &&
            this.y < other.y + other.h &&
            this.y + this.h > other.y
        );
    }
}

// EnvironmentObject class
class EnvironmentObject {
    constructor(x, y, w, h) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
        this.color = OBJECT_COLOR; // p5.js color object
    }

    draw() {
        fill(this.color);
        noStroke();
        rect(this.x, this.y, this.w, this.h);
    }
}

// CameraObject class
class CameraObject {
    constructor(x, y, w, h) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
        this.isHacked = false;
        this.normalColor = CAMERA_COLOR; // p5.js color object
        this.hackedColor = HACKED_CAMERA_COLOR; // p5.js color object
    }

    draw() {
        fill(this.isHacked ? this.hackedColor : this.normalColor);
        noStroke();
        rect(this.x, this.y, this.w, this.h);
    }

    hack() {
        this.isHacked = !this.isHacked;
    }
}

// SecurityZone class
class SecurityZone {
    constructor(x, y, w, h) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
        this.playerIsInside = false;
        this.normalColor = ZONE_NORMAL_COLOR_RGBA; // p5.js color object
        this.detectedColor = ZONE_DETECTED_COLOR_RGBA; // p5.js color object
    }

    update(playerObj) { // playerObj is an instance of Player
        // AABB collision check
        if (
            playerObj.x < this.x + this.w &&
            playerObj.x + playerObj.w > this.x &&
            playerObj.y < this.y + this.h &&
            playerObj.y + playerObj.h > this.y
        ) {
            this.playerIsInside = true;
        } else {
            this.playerIsInside = false;
        }
    }

    draw() {
        fill(this.playerIsInside ? this.detectedColor : this.normalColor);
        noStroke();
        rect(this.x, this.y, this.w, this.h);
    }
}


// Camera class for p5.js
class Camera {
    constructor(worldWidth, worldHeight) {
        this.x = 0;
        this.y = 0;
        this.worldWidth = worldWidth;
        this.worldHeight = worldHeight;
        // SCREEN_WIDTH and SCREEN_HEIGHT are global constants
    }

    // Update camera position to center the target (e.g., player)
    // targetX, targetY should be the center of the target
    update(targetX, targetY) {
        let camTargetX = targetX - SCREEN_WIDTH / 2;
        let camTargetY = targetY - SCREEN_HEIGHT / 2;

        // Clamp camera position to world boundaries
        this.x = max(0, camTargetX);
        this.y = max(0, camTargetY);

        if (this.x + SCREEN_WIDTH > this.worldWidth) {
            this.x = this.worldWidth - SCREEN_WIDTH;
        }
        if (this.y + SCREEN_HEIGHT > this.worldHeight) {
            this.y = this.worldHeight - SCREEN_HEIGHT;
        }

        // Handle cases where world is smaller than screen
        if (this.worldWidth < SCREEN_WIDTH) {
            this.x = (this.worldWidth - SCREEN_WIDTH) / 2;
        }
        if (this.worldHeight < SCREEN_HEIGHT) {
            this.y = (this.worldHeight - SCREEN_HEIGHT) / 2;
        }
    }

    // Apply camera transformation (translate the canvas)
    apply() {
        translate(-this.x, -this.y);
    }
}

// Key press handling for actions like hacking
function keyPressed() {
    if (key === 'h' || key === 'H') {
        if (player) { // Ensure player exists
            for (let camObj of cameraObjects) {
                if (player.collidesWith(camObj)) {
                    camObj.hack();
                    break; // Hack one camera at a time if overlapping multiple
                }
            }
        }
    }
    // return false; // Uncomment to prevent default browser behavior for handled keys if necessary
}
