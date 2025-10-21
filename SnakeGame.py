"""
Snake Xtreme (with game modes)
Modes: Easy, Medium, Hard, Endless
Controls:
  - Arrow keys or WASD to move
  - P to pause
  - Enter to select / restart
  - Esc to quit
"""

import pygame, random, sys, time

# ---- Init ----
pygame.init()
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_W, GRID_H = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Xtreme - Modes Edition")
CLOCK = pygame.time.Clock()
FPS = 60

# ---- High Scores ----
easy = 0
medium = 74
hard = 54
endless = 0

# ---- Colors ----
BLACK = (10, 10, 14)
NEON_COLORS = [
    (255, 80, 180), (80, 250, 255), (0, 255, 150),
    (255, 240, 90), (255, 150, 50), (180, 100, 255),
    (0, 255, 255), (255, 60, 60), (255, 0, 255)
]
NEON_CYAN, NEON_YELLOW, NEON_RED = (80,250,255), (255,240,90), (255,60,60)

# ---- Fonts ----
FONT = pygame.font.SysFont("Comic Sans MS", 26, bold=True)
BIG_FONT = pygame.font.SysFont("Comic Sans MS", 48, bold=True)

# ---- Game state ----
snake, snake_dir, snake_color = [], (1,0), random.choice(NEON_COLORS)
food, food_color = (0,0), random.choice(NEON_COLORS)
powerups, particles, power_effects = [], [], []
bg_particles = [{"x":random.randint(0,WIDTH),"y":random.randint(0,HEIGHT),
                 "size":random.randint(1,3),"speed":random.uniform(0.2,1.0),
                 "color":random.choice(NEON_COLORS)} for _ in range(90)]
score, level, base_speed, speed = 0, 1, 8, 8
game_over, paused = False, False
active_power, power_timer = None, 0
last_move_time, spawn_timer = time.time(), 0
mode = None

# ---- Helpers ----
def random_free_cell(occupied):
    for _ in range(5000):
        pos = (random.randrange(0, GRID_W), random.randrange(0, GRID_H))
        if pos not in occupied: return pos
    return (0,0)

def spawn_food():
    return random_free_cell(set(snake))

def spawn_powerup():
    return {"pos": random_free_cell(set(snake)|{food}),
            "type": random.choice(["slow","shrink","bonus"]),
            "color": random.choice(NEON_COLORS)}

def spawn_particles_at(x,y,color,count=18):
    for _ in range(count):
        particles.append({"x":x,"y":y,
            "dx":random.uniform(-2.2,2.2),"dy":random.uniform(-2.2,2.2),
            "life":random.randint(18,36),"color":color})

def spawn_power_effect(x,y,color,count=28):
    for _ in range(count):
        power_effects.append({"x":x,"y":y,
            "dx":random.uniform(-3,3),"dy":random.uniform(-3,3),
            "life":random.randint(20,46),"color":color})

def draw_text_center(txt,font,color,y):
    surf = font.render(txt,True,color)
    WIN.blit(surf,(WIDTH//2-surf.get_width()//2,y))

def should_move(current_speed):
    global last_move_time
    now = time.time()
    if now-last_move_time >= 1.0/max(0.1,current_speed):
        last_move_time = now
        return True
    return False

# ---- Rendering ----
def render():
    WIN.fill(BLACK)
    for s in bg_particles:
        pygame.draw.circle(WIN, s["color"], (int(s["x"]), int(s["y"])), s["size"])
    # food
    fx,fy = food
    pygame.draw.rect(WIN, food_color, (fx*CELL_SIZE+4,fy*CELL_SIZE+4,CELL_SIZE-8,CELL_SIZE-8),border_radius=6)
    # powerups
    for pu in powerups:
        px,py=pu["pos"]
        pygame.draw.rect(WIN, pu["color"], (px*CELL_SIZE+6,py*CELL_SIZE+6,CELL_SIZE-12,CELL_SIZE-12),border_radius=6)
        lbl=FONT.render(pu["type"][0].upper(),True,(0,0,0))
        WIN.blit(lbl,(px*CELL_SIZE+CELL_SIZE//2-lbl.get_width()//2,py*CELL_SIZE+CELL_SIZE//2-lbl.get_height()//2))
    # snake
    for i,(sx,sy) in enumerate(snake):
        color=snake_color if i==0 else NEON_COLORS[i%len(NEON_COLORS)]
        pygame.draw.rect(WIN,color,(sx*CELL_SIZE+2,sy*CELL_SIZE+2,CELL_SIZE-4,CELL_SIZE-4),border_radius=6)
    # particles
    for p in particles: pygame.draw.circle(WIN,p["color"],(int(p["x"]),int(p["y"])),2)
    for e in power_effects: pygame.draw.circle(WIN,e["color"],(int(e["x"]),int(e["y"])),3)
    # UI
    ui=FONT.render(f"Score:{score}  Level:{level}  Speed:{speed}",True,NEON_CYAN)
    WIN.blit(ui,(10,8))
    if paused: draw_text_center("PAUSED",BIG_FONT,NEON_YELLOW,HEIGHT//2)
    if game_over:
        draw_text_center("GAME OVER",BIG_FONT,NEON_RED,HEIGHT//2-50)
        draw_text_center("Press ENTER to restart or ESC to quit",FONT,NEON_CYAN,HEIGHT//2+20)
    pygame.display.flip()

# ---- Menu ----
def menu():
    global mode
    options=["Easy","Medium","Hard","Endless"]
    selected=0
    while True:
        WIN.fill(BLACK)
        draw_text_center("SNAKE XTREME",BIG_FONT,NEON_YELLOW,120)
        for i,opt in enumerate(options):
            color=NEON_COLORS[i%len(NEON_COLORS)] if i==selected else (180,180,180)
            draw_text_center(opt,FONT,color,240+i*50)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit();sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key in (pygame.K_UP,pygame.K_w): selected=(selected-1)%len(options)
                if e.key in (pygame.K_DOWN,pygame.K_s): selected=(selected+1)%len(options)
                if e.key==pygame.K_RETURN:
                    mode=options[selected].lower()
                    return

# ---- Reset ----
def reset_game():
    global snake,snake_dir,snake_color,food,food_color,powerups,particles,power_effects
    global score,level,base_speed,speed,game_over,paused
    snake=[(GRID_W//2,GRID_H//2),(GRID_W//2-1,GRID_H//2),(GRID_W//2-2,GRID_H//2)]
    snake_dir=(1,0)
    snake_color=random.choice(NEON_COLORS)
    food=spawn_food(); food_color=random.choice(NEON_COLORS)
    powerups,particles,power_effects=[],[],[]
    score,level=0,1
    game_over,paused=False,False
    if mode=="easy": base_speed=6
    elif mode=="medium": base_speed=8
    elif mode=="hard": base_speed=12
    elif mode=="endless": base_speed=5
    speed=base_speed

# ---- Main Loop ----
menu(); reset_game()
running=True
while running:
    dt=CLOCK.tick(FPS)
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.KEYDOWN:
            if e.key in (pygame.K_UP,pygame.K_w) and snake_dir!=(0,1): snake_dir=(0,-1)
            elif e.key in (pygame.K_DOWN,pygame.K_s) and snake_dir!=(0,-1): snake_dir=(0,1)
            elif e.key in (pygame.K_LEFT,pygame.K_a) and snake_dir!=(1,0): snake_dir=(-1,0)
            elif e.key in (pygame.K_RIGHT,pygame.K_d) and snake_dir!=(-1,0): snake_dir=(1,0)
            elif e.key==pygame.K_p: paused=not paused
            elif e.key==pygame.K_RETURN and game_over: reset_game()
            elif e.key==pygame.K_ESCAPE: running=False
    if not running: break

    if not paused and not game_over:
        # update bg
        for s in bg_particles:
            s["y"]+=s["speed"]; 
            if s["y"]>HEIGHT: s["y"]=0; s["x"]=random.randint(0,WIDTH)
        # move?
        if should_move(speed):
            hx,hy=snake[0]; dx,dy=snake_dir
            new_head=((hx+dx)%GRID_W,(hy+dy)%GRID_H)
            if new_head in snake and mode!="endless": game_over=True
            else:
                snake.insert(0,new_head)
                if new_head==food:
                    score+=1
                    spawn_particles_at(new_head[0]*CELL_SIZE,new_head[1]*CELL_SIZE,food_color,20)
                    food=spawn_food(); food_color=random.choice(NEON_COLORS)
                    if random.random()<0.2: powerups.append(spawn_powerup())
                    if score%5==0: level+=1; base_speed+=1; speed=base_speed
                else: snake.pop()
                for pu in powerups[:]:
                    if new_head==pu["pos"]:
                        spawn_power_effect(new_head[0]*CELL_SIZE,new_head[1]*CELL_SIZE,pu["color"])
                        if pu["type"]=="slow": base_speed=max(3,base_speed-2)
                        elif pu["type"]=="shrink" and len(snake)>5: snake=snake[:-3]
                        elif pu["type"]=="bonus": score+=5
                        powerups.remove(pu)
    render()

pygame.quit(); sys.exit()
