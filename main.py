import time
from collections import namedtuple

import pygame as pg

class Vector:
    def __init__(self, *, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, v):
        if not isinstance(v, Vector):
            return False

        is_x_equal = self.x == v.x
        is_y_equal = self.y == v.y

        if is_x_equal and is_y_equal:
            return True

        return False

    def __add__(self, v):
        if not isinstance(v, Vector):
            return False

        return Vector(x=self.x + v.x, y=self.y + v.y)

    def __sub__(self, v):
        if not isinstance(v, Vector):
            return False
        
        return Vector(x=self.x - v.x, y=self.y - v.y)

class Block:
    def __init__(self, *, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def __repr__(self):
        return f'Block({self.to_dict()})'

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h
        }

    def rect(self, *, x=0, y=0, scale=1):
        return pg.Rect(
            x + self.x * scale,
            y + self.y * scale,
            self.w * scale,
            self.h * scale
        )

    def render(self, screen, color, *, x=0, y=0, scale=1, width=0):
        pg.draw.rect(screen, color.v(), self.rect(x=x, y=y, scale=scale), width=width)

class Color:
    def __init__(self, *, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def v(self):
        return (self.r, self.g, self.b)
    
    def __repr__(self):
        return f'{self.v()}'

class Canvas:
    def __init__(self, *, x=0, y=0, h, w, scale=1, center=False):
        self.w = w
        self.h = h
        self.scale = scale
        self.center = center
        
        self.p_0 = None
        self.p_1 = None

        if self.center:
            self.x = x - (w * scale) / 2
            self.y = y - (h * scale) / 2
        else:
            self.x = x
            self.y = y

        self.rows = []
        self.render_cells = []

        color = Color(r=255, g=255, b=255)

        for y_index in range(h):
            self.rows.append([])
            for x_index in range(w):
                self.render_cells.append(Vector(x=x_index, y=y_index))
                self.rows[y_index].append(color)


    def rect(self):
        return pg.Rect(
            self.x,
            self.y,
            self.w * self.scale,
            self.h * self.scale
        )

    def set_pixel(self, color, *, x, y):
        if (x < 0 or x >= self.w) or (y < 0 or y >= self.h):
            return

        self.render_cells.append(Vector(x=x, y=y))
        self.rows[y][x] = color

    def draw(self, color, *, x, y):
        self.p_1 = Vector(x=x, y=y)

        if not self.p_0:
            self.p_0 = Vector(x=x, y=y)

        if self.p_0 != self.p_1:

            diff = self.p_1 - self.p_0

            if diff.x == 0:

                if diff.y > 0:
                    steps = range(self.p_0.y, self.p_1.y)
                else:
                    steps = range(self.p_1.y, self.p_0.y)

                for i in steps:
                    self.set_pixel(color, x=self.p_0.x, y=i)
            elif diff.y == 0:
                if diff.x > 0:
                    steps = range(self.p_0.x, self.p_1.x)
                else:
                    steps = range(self.p_1.x, self.p_0.x)

                for i in steps:
                    self.set_pixel(color, x=i, y=self.p_0.y)

            elif abs(diff.x) == abs(diff.y):
                m = diff.y / diff.x
                b = self.p_0.y - m * self.p_0.x
                if diff.x > 0:
                    steps = range(self.p_0.x, self.p_1.x)
                else:
                    steps = range(self.p_1.x, self.p_0.x)

                for i in steps:
                    y_index = int(m * i + b)
                    self.set_pixel(color, x=i, y=y_index)

            elif abs(diff.x) > abs(diff.y):
                m = diff.y / diff.x
                b = self.p_0.y - m * self.p_0.x

                if diff.x > 0:
                    steps = range(self.p_0.x, self.p_1.x)
                else:
                    steps = range(self.p_1.x, self.p_0.x)

                for i in steps:
                    y_index = int(m * i + b)

                    self.set_pixel(color, x=i, y=y_index)
            elif abs(diff.x) < abs(diff.y):
                m = diff.y / diff.x
                m_inv = diff.x / diff.y
                b = self.p_0.y - m * self.p_0.x

                if diff.y > 0:
                    steps = range(self.p_0.y, self.p_1.y)
                else:
                    steps = range(self.p_1.y, self.p_0.y)

                for i in steps:
                    x_index = int(m_inv * i - m_inv * b)

                    self.set_pixel(color, x=x_index, y=i)
        else:
            self.set_pixel(color, x=self.p_1.x, y=self.p_1.y)

    def render(self, screen, *, x=0, y=0):
        for p in self.render_cells:
            pixel = self.rows[p.y][p.x]

            rect = pg.Rect(
                x + self.x + p.x * self.scale,
                y + self.y + p.y * self.scale,
                self.scale,
                self.scale
            )
            pg.draw.rect(screen, pixel.v(), rect)
        
        self.render_cells = []

class Key:

    def __init__(self):
        self.state = False
        self.press = False
        self._flag = False

    def update(self, state):
        self.state = bool(state)

        if self.state and not self._flag:
            self.press = True
            self._flag = True
        elif not self.state and self._flag:
            self.press = False
            self._flag = False
        else:
            self.press = False

    def __repr__(self):
        return f'{self.state} - {self.press}'

class Mouse(Block):
    def __init__(self):
        super(Mouse, self).__init__(x=0, y=0, w=1, h=1)

        Buttons = namedtuple(
            'Buttons',
            ['left', 'middle', 'right'],
            defaults=[Key(), Key(), Key()]
        )

        self.button = Buttons()

    
    def update(self):
        self.x, self.y = pg.mouse.get_pos()
        left, middle, right = pg.mouse.get_pressed()

        self.button.left.update(left)
        self.button.middle.update(middle)
        self.button.right.update(right)

def check_collition(A, B):
    # A Edges
    A_IZQ = A.x
    A_DER = A.x + A.w
    A_ARR = A.y
    A_ABJ = A.y + A.h

    # B Edges
    B_IZQ = B.x
    B_DER = B.x + B.w
    B_ARR = B.y
    B_ABJ = B.y + B.h

    # Restrictions
    return (
        (A_ABJ >= B_ARR) and
        (A_ARR <= B_ABJ) and
        (A_DER >= B_IZQ) and
        (A_IZQ <= B_DER)
    )



pg.init()
width = 800
height = 600
screen = pg.display.set_mode((width, height))
mouse = Mouse()

canvas = Canvas(x=width/2, y=height/2, w=790, h=590, scale=1, center=True)

game_exit = False

paint_color = Color(r=0, g=0, b=0)
screen.fill((50, 50, 50))
while not game_exit:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            game_exit = True
    
    mouse.update()

    if mouse.button.left.state:

        if check_collition(mouse.rect(), canvas.rect()):

            canvas.draw(
                paint_color,
                x=int((mouse.rect().x - canvas.x) / canvas.scale),
                y=int((mouse.rect().y - canvas.y) / canvas.scale)
            )
        else:
            canvas.p_0 = None
            canvas.p_1 = None

        canvas.p_0 = canvas.p_1
    else:
        canvas.p_0 = None
        canvas.p_1 = None


    canvas.render(screen)

    pg.display.flip()

pg.quit()