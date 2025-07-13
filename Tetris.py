import pygame
import random
import sys
import time

pygame.init()
FONT = pygame.font.SysFont("Courier", 20)

CELL = 20
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game constants
BOARD_WIDTH = 12
BOARD_HEIGHT = 22
TICK_RATE = 0.625  # slowed 20% for normal falling


INV_WIDTH = 60
INV_HEIGHT = 20
INV_TICK = 0.2
ALIEN_WIDTH = 3

CLIMB_WIDTH = 30
CLIMB_VISIBLE = 20
CLIMB_JUMP = 4
CLIMB_TICK = 0.05

PAC_TICK = 0.2
PAC_LAYOUT = [
    "####################",
    "#P.......##........#",
    "#.####.#.##.#.####.#",
    "#.#....G.....#.#.#.#",
    "#.#.##########.#.#.#",
    "#.#............#.#.#",
    "#.####.######.####.#",
    "#........##........#",
    "####################",
]
PAC_HEIGHT = len(PAC_LAYOUT)
PAC_WIDTH = len(PAC_LAYOUT[0])


def draw_text(surface, text, x, y, color=WHITE):
    img = FONT.render(text, True, color)
    surface.blit(img, (x, y))


# ------------------ TETRIS ------------------
PIECES = {
    'I': [
        [(0,1),(1,1),(2,1),(3,1)],
        [(2,0),(2,1),(2,2),(2,3)],
        [(0,2),(1,2),(2,2),(3,2)],
        [(1,0),(1,1),(1,2),(1,3)],
    ],
    'O': [[(1,0),(2,0),(1,1),(2,1)]]*4,
    'T': [
        [(1,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(2,1),(1,2)],
        [(1,0),(0,1),(1,1),(1,2)],
    ],
    'S': [
        [(1,0),(2,0),(0,1),(1,1)],
        [(1,0),(1,1),(2,1),(2,2)],
        [(1,1),(2,1),(0,2),(1,2)],
        [(0,0),(0,1),(1,1),(1,2)],
    ],
    'Z': [
        [(0,0),(1,0),(1,1),(2,1)],
        [(2,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(1,2),(2,2)],
        [(1,0),(0,1),(1,1),(0,2)],
    ],
    'J': [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,2)],
        [(1,0),(1,1),(0,2),(1,2)],
    ],
    'L': [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,1),(1,1),(2,1),(0,2)],
        [(0,0),(1,0),(1,1),(1,2)],
    ],
}
PIECE_COLORS = {
    'I': (0,255,255),
    'O': (255,255,0),
    'T': (128,0,128),
    'S': (0,255,0),
    'Z': (255,0,0),
    'J': (0,0,255),
    'L': (255,165,0),
}

class Piece:
    def __init__(self, name):
        self.name = name
        self.rotation = 0
        self.coords = PIECES[name]
        self.x = BOARD_WIDTH//2 - 2
        self.y = 0

    def cells(self, rot=None, dx=0, dy=0):
        r = self.rotation if rot is None else rot
        return [(x+self.x+dx, y+self.y+dy) for x,y in self.coords[r%4]]

class Tetris:
    def __init__(self):
        self.board = [[None]*BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.game_over = False
        self.last_drop = time.time()

    def new_piece(self):
        return Piece(random.choice(list(PIECES)))

    def check(self, cells):
        for x,y in cells:
            if x<0 or x>=BOARD_WIDTH or y>=BOARD_HEIGHT:
                return True
            if y>=0 and self.board[y][x]:
                return True
        return False

    def lock(self):
        for x,y in self.current.cells():
            if 0<=y<BOARD_HEIGHT:
                self.board[y][x]=self.current.name
        self.clear_lines()
        self.current = self.next_piece
        self.next_piece = self.new_piece()
        if self.check(self.current.cells()):
            self.game_over=True

    def clear_lines(self):
        new = [row for row in self.board if not all(row)]
        lines = BOARD_HEIGHT - len(new)
        for _ in range(lines):
            new.insert(0, [None]*BOARD_WIDTH)
        self.board = new
        self.score += lines * 100

    def move(self,dx,dy):
        if not self.check(self.current.cells(dx=dx, dy=dy)):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def rotate(self, direction=1):
        """Rotate the current piece. direction=1 for clockwise, -1 for counter."""
        r=(self.current.rotation+direction)%4
        if not self.check(self.current.cells(rot=r)):
            self.current.rotation=r

    def step(self):
        if time.time()-self.last_drop>TICK_RATE:
            if not self.move(0,1):
                self.lock()
            self.last_drop=time.time()

    def draw(self,screen):
        screen.fill(BLACK)
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                name=self.board[y][x]
                if name:
                    pygame.draw.rect(screen,PIECE_COLORS[name],(x*CELL,y*CELL,CELL,CELL))
        for x,y in self.current.cells():
            if y>=0:
                pygame.draw.rect(screen,PIECE_COLORS[self.current.name],(x*CELL,y*CELL,CELL,CELL))
        # Outline the playing field
        pygame.draw.rect(screen, WHITE, (0, 0, BOARD_WIDTH*CELL, BOARD_HEIGHT*CELL), 2)

        # draw next piece preview at top of right column
        draw_text(screen, "Next:", BOARD_WIDTH*CELL + 10, 20)
        for x, y in PIECES[self.next_piece.name][0]:
            pygame.draw.rect(
                screen,
                PIECE_COLORS[self.next_piece.name],
                (BOARD_WIDTH*CELL + 40 + x*CELL, 50 + y*CELL, CELL, CELL),
            )

        # draw score at bottom of right column
        draw_text(
            screen,
            f"Score: {self.score}",
            BOARD_WIDTH*CELL + 10,
            BOARD_HEIGHT*CELL - 40,
        )
        if self.game_over:
            draw_text(screen,"GAME OVER",BOARD_WIDTH*CELL//2-60,BOARD_HEIGHT*CELL//2)
        pygame.display.flip()

    def run(self):
        screen=pygame.display.set_mode((BOARD_WIDTH*CELL+200,BOARD_HEIGHT*CELL))
        clock=pygame.time.Clock()
        last_move={pygame.K_LEFT:0,pygame.K_RIGHT:0,pygame.K_DOWN:0}
        MOVE_INTERVAL=0.15
        LR_INTERVAL=MOVE_INTERVAL/1.2
        DOWN_INTERVAL=MOVE_INTERVAL/3  # 1.5× faster drop when holding down
        while not self.game_over:
            now=time.time()
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_LEFT:
                        self.move(-1,0)
                        last_move[pygame.K_LEFT]=now
                    elif e.key==pygame.K_RIGHT:
                        self.move(1,0)
                        last_move[pygame.K_RIGHT]=now
                    elif e.key==pygame.K_DOWN:
                        if not self.move(0,1):
                            self.lock()
                        last_move[pygame.K_DOWN]=now
                    elif e.key==pygame.K_a:
                        # Swapped rotation direction: 'a' now rotates clockwise
                        self.rotate(1)
                    elif e.key==pygame.K_d:
                        # Swapped rotation direction: 'd' now rotates counter-clockwise
                        self.rotate(-1)
                    elif e.key==pygame.K_q:
                        return
            keys=pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and now-last_move[pygame.K_LEFT]>=LR_INTERVAL:
                if self.move(-1,0):
                    last_move[pygame.K_LEFT]=now
            if keys[pygame.K_RIGHT] and now-last_move[pygame.K_RIGHT]>=LR_INTERVAL:
                if self.move(1,0):
                    last_move[pygame.K_RIGHT]=now
            if keys[pygame.K_DOWN] and now-last_move[pygame.K_DOWN]>=DOWN_INTERVAL:
                if not self.move(0,1):
                    self.lock()
                last_move[pygame.K_DOWN]=now
            self.step()
            self.draw(screen)
            clock.tick(60)
        waiting=True
        while waiting:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN:
                    waiting=False
            clock.tick(30)



# Remaining games would be similarly converted using pygame.


def start_menu():
    screen=pygame.display.set_mode((640,480))
    clock=pygame.time.Clock()
    options=["Play Tetris","Quit"]
    idx=0
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_UP:
                    idx=(idx-1)%len(options)
                elif e.key==pygame.K_DOWN:
                    idx=(idx+1)%len(options)
                elif e.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                    return idx
        screen.fill(BLACK)
        draw_text(screen,"Select a game:",40,40)
        for i,opt in enumerate(options):
            prefix="-> " if i==idx else "   "
            draw_text(screen,prefix+opt,60,80+i*30)
        pygame.display.flip()
        clock.tick(30)


def main():
    while True:
        choice=start_menu()
        if choice==0:
            Tetris().run()
        else:
            break

if __name__=="__main__":
    main()
