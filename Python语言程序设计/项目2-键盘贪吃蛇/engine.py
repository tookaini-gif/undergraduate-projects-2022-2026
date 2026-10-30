"""Pure game rules, independent from the Pygame display."""
import random

class Snake:
    def __init__(self, width=30, height=20, seed=None):
        if width < 4 or height < 2: raise ValueError('Board must be at least 4 by 2')
        self.width, self.height = width, height
        self.rng = random.Random(seed)
        self.reset()
    def reset(self):
        self.body = [(3, self.height//2), (2, self.height//2), (1, self.height//2)]
        self.direction = (1, 0); self.score = 0; self.over = False; self.won = False
        self.food = self.new_food()
    def new_food(self):
        free = [(x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in self.body]
        return self.rng.choice(free) if free else None
    def step(self, requested=None):
        if self.over: return
        if requested in {(1, 0), (-1, 0), (0, 1), (0, -1)}:
            if requested != (-self.direction[0], -self.direction[1]): self.direction = requested
        x, y = self.body[0]; dx, dy = self.direction; head = (x+dx, y+dy)
        eating = head == self.food
        occupied = self.body if eating else self.body[:-1]
        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height) or head in occupied:
            self.over = True; return
        self.body.insert(0, head)
        if eating:
            self.score += 10; self.food = self.new_food()
            if self.food is None: self.over = True; self.won = True
        else: self.body.pop()
