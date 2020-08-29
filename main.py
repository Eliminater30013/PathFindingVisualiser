import pygame
import math
from queue import PriorityQueue

WIDTH = 670  # width of window
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)  # if its red, we have already visited this node
GREEN = (0, 255, 0)  # the next nodes we are visiting
BLUE = (0, 255, 0)  # colour change
YELLOW = (255, 255, 0)  # colour change
WHITE = (255, 255, 255)  # white we haven't visited the spot yet
BLACK = (0, 0, 0)  # black means its a border/barrier
PURPLE = (128, 0, 128)  # purple is the path from start to end
ORANGE = (255, 165, 0)  # orange is the start node
GREY = (128, 128, 128)  # for lines in the grid
TURQUOISE = (64, 224, 208)  # for end point


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.colour = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    # getters

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.colour == RED

    def is_open(self):
        return self.colour == GREEN

    def is_barrier(self):
        return self.colour == BLACK

    def is_start(self):
        return self.colour == ORANGE

    def is_end(self):
        return self.colour == TURQUOISE

    # Setters

    def reset(self):
        self.colour = WHITE

    def make_closed(self):
        self.colour = RED

    def make_open(self):
        self.colour = GREEN

    def make_barrier(self):
        self.colour = BLACK

    def make_start(self):
        self.colour = ORANGE

    def make_end(self):
        self.colour = TURQUOISE

    def make_path(self):
        self.colour = PURPLE

    # Methods

    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []
        ''' Moving down/up a row, check if we can move down/up (if not barrier below/above/left/right, make it out 
            neighbour '''
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # check below
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # check above
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # check right
            self.neighbours.append(grid[self.row][self.col + 1])

        if self.row > 0 and not grid[self.row][self.col - 1].is_barrier():  # check left
            self.neighbours.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def heuristic(p1, p2):  # ((x1,y1)(x2,y2))
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:  # traverse the path backwards
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}  # dict for path
    g_score = {spot: float("inf") for row in grid for spot in row}  # init
    g_score[start] = 0  # start -> start = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())  # start->end estimate
    open_set_hash = {start}  # allows us to keep track of what is in the queue in the form of a hash map
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # allows us to exit the loop of anything goes wrong
                pygame.quit()
        current = open_set.get()[2]  # getNode
        open_set_hash.remove(current)  # sync with queue
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + heuristic(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
        draw()
        if current != start:  # if the node has already been considered close it
            current.make_closed()
    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    game_is_running = True
    while game_is_running:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():  # an event can be mouse click/keyboard input
            if event.type == pygame.QUIT:
                game_is_running = False
            if pygame.mouse.get_pressed()[0]:  # left button aka draw the spot
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()
            elif pygame.mouse.get_pressed()[2]:  # right button aka delete button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:  # make sure to reset the variables after deletion for start and end
                    start = None
                if spot == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    pygame.quit()


main(WIN, WIDTH)
