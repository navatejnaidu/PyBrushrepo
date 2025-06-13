import pygame
import sys
import math
from collections import deque  # Needed for efficient flood fill

# Initialize Pygame library
pygame.init()

# ====================
# CONSTANT DEFINITIONS
# ====================
WIDTH, HEIGHT = 1000, 700  # Main window dimensions
CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600  # Drawing area dimensions
TOOLBAR_WIDTH = 200  # Width of the tools panel
COLORS_PER_ROW = 5  # Colors per row in palette
BRUSH_SIZES = [1, 3, 5, 8, 12, 18, 25]  # Available brush sizes

# Color definitions (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)
BROWN = (165, 42, 42)
CYAN = (0, 255, 255)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)

# ==================
# SETUP & INITIALIZE
# ==================
# Create main window and drawing canvas
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Paint")
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill(WHITE)  # Start with white background

# Drawing state variables
drawing = False  # True when mouse is pressed
last_pos = None  # Previous mouse position (for continuous drawing)
current_color = BLACK  # Currently selected color
current_tool = "pencil"  # Active tool (pencil, eraser, line, etc.)
brush_size = 5  # Current brush thickness
start_pos = None  # Starting point for shapes
temp_surface = None  # Temporary canvas for previewing shapes

# Available colors in palette
palette_colors = [
    BLACK, RED, GREEN, BLUE, YELLOW,
    PURPLE, ORANGE, PINK, BROWN, CYAN,
    LIGHT_BLUE, LIGHT_GREEN, WHITE, LIGHT_GRAY, DARK_GRAY
]

# Tool definitions with icons
tools = [
    {"name": "pencil", "icon": "✏️"},
    {"name": "eraser", "icon": "🧹"},
    {"name": "line", "icon": "📏"},
    {"name": "rectangle", "icon": "⬜"},
    {"name": "circle", "icon": "⭕"},
    {"name": "fill", "icon": "🪣"}
]

# Font setup
font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 24)


# ==============
# UI COMPONENTS
# ==============
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)  # Clickable area
        self.text = text
        self.color = color
        self.hover_color = hover_color  # Color when mouse hovers
        self.text_color = text_color
        self.hover = False  # Hover state

    def draw(self, surface):
        """Draw button on screen"""
        color = self.hover_color if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2)  # Border

        # Add text if exists
        if self.text:
            text_surface = small_font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        """Update hover state based on mouse position"""
        self.hover = self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


# Create UI buttons for colors, tools, and sizes
color_buttons = []
for i, color in enumerate(palette_colors):
    row = i // COLORS_PER_ROW
    col = i % COLORS_PER_ROW
    btn = Button(
        WIDTH - TOOLBAR_WIDTH + 20 + col * 35,
        100 + row * 35,
        30, 30, "", color, color
    )
    color_buttons.append(btn)

# Tool buttons
tool_buttons = []
for i, tool in enumerate(tools):
    btn = Button(
        WIDTH - TOOLBAR_WIDTH + 20 + (i % 3) * 60,
        250 + (i // 3) * 50,
        50, 40, tool["icon"], LIGHT_GRAY, WHITE
    )
    tool_buttons.append(btn)

# Brush size buttons
brush_buttons = []
for i, size in enumerate(BRUSH_SIZES):
    row = i // 4
    col = i % 4
    btn = Button(
        WIDTH - TOOLBAR_WIDTH + 20 + col * 45,
        400 + row * 40,
        40, 30, f"{size}", LIGHT_GRAY, WHITE
    )
    brush_buttons.append(btn)

# Clear button
clear_button = Button(WIDTH - TOOLBAR_WIDTH + 20, 550, 160, 40, "Clear Canvas", LIGHT_GRAY, WHITE)


# ====================
# DRAWING FUNCTIONS
# ====================
def draw_pencil(pos, size):
    """Draw circle at current position"""
    pygame.draw.circle(canvas, current_color, pos, size)


def draw_eraser(pos, size):
    """Erase by drawing with background color"""
    pygame.draw.circle(canvas, WHITE, pos, size)


def draw_line(start, end, size):
    """Draw straight line between two points"""
    pygame.draw.line(canvas, current_color, start, end, size)


def draw_rectangle(start, end, size):
    """Draw rectangle outline"""
    rect = pygame.Rect(min(start[0], end[0]), min(start[1], end[1]),
                       abs(end[0] - start[0]), abs(end[1] - start[1]))
    pygame.draw.rect(canvas, current_color, rect, size)


def draw_circle(start, end, size):
    """Draw circle outline"""
    radius = int(math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2))
    pygame.draw.circle(canvas, current_color, start, radius, size)


def fill_bucket(pos):
    """Flood fill area using queue-based algorithm"""
    target_color = canvas.get_at(pos)
    if target_color == current_color:
        return

    # Use queue for efficient flood fill
    queue = deque([pos])
    visited = set([pos])

    while queue:
        x, y = queue.popleft()
        if not (0 <= x < CANVAS_WIDTH and 0 <= y < CANVAS_HEIGHT):
            continue

        if canvas.get_at((x, y)) == target_color:
            canvas.set_at((x, y), current_color)
            # Check all adjacent positions
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                new_pos = (x + dx, y + dy)
                if new_pos not in visited:
                    visited.add(new_pos)
                    queue.append(new_pos)


# ====================
# MAIN APPLICATION LOOP
# ====================
clock = pygame.time.Clock()  # For controlling frame rate

while True:
    # Get mouse position and adjust for canvas
    mouse_pos = pygame.mouse.get_pos()
    # Only use positions within canvas bounds
    canvas_mouse_pos = (mouse_pos[0], mouse_pos[1]) if 0 <= mouse_pos[0] < CANVAS_WIDTH and 0 <= mouse_pos[
        1] < CANVAS_HEIGHT else None

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Canvas interaction
        if canvas_mouse_pos:
            # Mouse press: Start drawing action
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                drawing = True
                last_pos = canvas_mouse_pos
                start_pos = canvas_mouse_pos

                # Special handling for certain tools
                if current_tool == "fill":
                    fill_bucket(canvas_mouse_pos)
                elif current_tool in ["line", "rectangle", "circle"]:
                    temp_surface = canvas.copy()  # Store current canvas state

            # Mouse release: Finish drawing action
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drawing = False

                # Finalize shape drawing
                if current_tool == "line" and start_pos and temp_surface:
                    canvas.blit(temp_surface, (0, 0))
                    draw_line(start_pos, canvas_mouse_pos, brush_size)
                    temp_surface = None
                elif current_tool == "rectangle" and start_pos and temp_surface:
                    canvas.blit(temp_surface, (0, 0))
                    draw_rectangle(start_pos, canvas_mouse_pos, brush_size)
                    temp_surface = None
                elif current_tool == "circle" and start_pos and temp_surface:
                    canvas.blit(temp_surface, (0, 0))
                    draw_circle(start_pos, canvas_mouse_pos, brush_size)
                    temp_surface = None
                last_pos = None

        # Handle UI button interactions
        # Color buttons
        for btn in color_buttons:
            btn.check_hover(mouse_pos)
            if btn.is_clicked(mouse_pos, event):
                current_color = btn.color

        # Tool buttons
        for i, btn in enumerate(tool_buttons):
            btn.check_hover(mouse_pos)
            if btn.is_clicked(mouse_pos, event):
                current_tool = tools[i]["name"]

        # Brush size buttons
        for i, btn in enumerate(brush_buttons):
            btn.check_hover(mouse_pos)
            if btn.is_clicked(mouse_pos, event):
                brush_size = BRUSH_SIZES[i]

        # Clear canvas button
        clear_button.check_hover(mouse_pos)
        if clear_button.is_clicked(mouse_pos, event):
            canvas.fill(WHITE)

    # Continuous drawing (for pencil/eraser)
    if drawing and canvas_mouse_pos:
        if current_tool == "pencil":
            if last_pos:
                draw_line(last_pos, canvas_mouse_pos, brush_size)
            else:
                draw_pencil(canvas_mouse_pos, brush_size)
            last_pos = canvas_mouse_pos
        elif current_tool == "eraser":
            if last_pos:
                draw_line(last_pos, canvas_mouse_pos, brush_size)
            else:
                draw_eraser(canvas_mouse_pos, brush_size)
            last_pos = canvas_mouse_pos

    # ======================
    # RENDER THE APPLICATION
    # ======================
    screen.fill(GRAY)  # Background

    # Draw canvas area
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT))
    screen.blit(canvas, (0, 0))

    # Draw toolbar
    pygame.draw.rect(screen, LIGHT_GRAY, (CANVAS_WIDTH, 0, TOOLBAR_WIDTH, HEIGHT))
    pygame.draw.line(screen, DARK_GRAY, (CANVAS_WIDTH, 0), (CANVAS_WIDTH, HEIGHT), 2)

    # Draw title
    title = font.render("PyGame Paint", True, BLACK)
    screen.blit(title, (CANVAS_WIDTH + 20, 20))

    # Draw color palette
    colors_title = font.render("Colors:", True, BLACK)
    screen.blit(colors_title, (CANVAS_WIDTH + 20, 70))
    for btn in color_buttons:
        btn.draw(screen)

    # Highlight selected color
    pygame.draw.rect(screen, BLACK, (CANVAS_WIDTH + 20, 180, 160, 30), 2)
    pygame.draw.rect(screen, current_color, (CANVAS_WIDTH + 25, 185, 150, 20))

    # Draw tools
    tools_title = font.render("Tools:", True, BLACK)
    screen.blit(tools_title, (CANVAS_WIDTH + 20, 220))
    for i, btn in enumerate(tool_buttons):
        btn.draw(screen)
        # Highlight selected tool
        if current_tool == tools[i]["name"]:
            pygame.draw.rect(screen, BLUE, btn.rect, 3)

    # Draw brush sizes
    brush_title = font.render("Brush Size:", True, BLACK)
    screen.blit(brush_title, (CANVAS_WIDTH + 20, 370))
    for i, btn in enumerate(brush_buttons):
        btn.draw(screen)
        # Highlight selected size
        if brush_size == BRUSH_SIZES[i]:
            pygame.draw.rect(screen, BLUE, btn.rect, 3)

    # Draw current brush preview
    preview_text = font.render("Current Brush:", True, BLACK)
    screen.blit(preview_text, (CANVAS_WIDTH + 20, 480))
    pygame.draw.circle(screen, current_color, (CANVAS_WIDTH + 100, 520), brush_size)
    pygame.draw.circle(screen, BLACK, (CANVAS_WIDTH + 100, 520), brush_size, 1)

    # Draw clear button
    clear_button.draw(screen)

    # Draw instructions
    instructions = [
        "Instructions:",
        "- Click and drag to draw",
        "- Select a tool from the left",
        "- Change brush size as needed",
        "- Use fill tool to fill areas",
        "- Clear button resets canvas"
    ]
    for i, line in enumerate(instructions):
        text = small_font.render(line, True, BLACK)
        screen.blit(text, (CANVAS_WIDTH + 20, 600 + i * 25))

    # Draw temporary shape preview
    if drawing and temp_surface and start_pos and canvas_mouse_pos:
        screen.blit(temp_surface, (0, 0))
        if current_tool == "line":
            pygame.draw.line(screen, current_color, start_pos, canvas_mouse_pos, brush_size)
        elif current_tool == "rectangle":
            rect = pygame.Rect(min(start_pos[0], canvas_mouse_pos[0]),
                               min(start_pos[1], canvas_mouse_pos[1]),
                               abs(canvas_mouse_pos[0] - start_pos[0]),
                               abs(canvas_mouse_pos[1] - start_pos[1]))
            pygame.draw.rect(screen, current_color, rect, brush_size)
        elif current_tool == "circle":
            radius = int(math.sqrt((canvas_mouse_pos[0] - start_pos[0]) ** 2 +
                                   (canvas_mouse_pos[1] - start_pos[1]) ** 2))
            pygame.draw.circle(screen, current_color, start_pos, radius, brush_size)

    pygame.display.flip()  # Update display
    clock.tick(60)  # Maintain 60 FPS
