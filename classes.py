import itertools
import queue
import threading

import numpy as np
import pygame as pg

import maze.stuff as stuff
import myutil.eventman as eventman
from maze.constants import COLORMAP


class Taskman:
    def __init__(self):
        self.tasks = set()

    def add(self, cor):
        self.tasks.add(cor)
        return cor

    def update(self):
        for cor in self.tasks:
            try:
                next(cor)
            except StopIteration:
                self.tasks.remove(cor)


class World:
    keep_running = True

    def __init__(self, cellsize: int, cellshape: tuple[int]):
        self.CS = cellsize
        self.shape = cellshape
        surface = pg.display.get_surface()
        self.cellsurf = surface.copy()
        self.q = queue.Queue(2)
        self.th = threading.Thread(target=self.maze_produce, daemon=True)
        self.th.start()
        self.__listener = [
            eventman.addlistener(pg.KEYDOWN, self.keydown),
            eventman.addlistener(pg.QUIT, self.quit),
            eventman.addlistener(pg.MOUSEMOTION, self.mousemotion),
        ]

    def maze_produce(self):
        while self.keep_running:
            field = np.ones(self.shape, 'uint8')
            start, goal = stuff.maze_build(field)
            route1 = list(stuff.maze_solver(
                field, start, goal, depthfirst=True))
            route2 = list(stuff.maze_solver(field, start, goal))
            if len(route1) != len(route2):
                self.q.put((field, route1, route2))

    def set_field(self, field):
        self.field = field
        surf = self.cellsurf
        surf.fill((0, 0, 0))
        for pos in itertools.product(*map(range, field.shape)):
            v = field[pos]
            self.drawcell(surf, pos, COLORMAP[v])
        self.prev_field = field.copy()

    def update_cellsurf(self):
        field = self.field
        surf = self.cellsurf
        for pos in zip(*np.where(field != self.prev_field)):
            v = field[pos]
            self.drawcell(surf, pos, COLORMAP[v])
        self.prev_field = field.copy()

    def toscreen(self, cellpos):
        CS = self.CS
        CH, CW = self.shape
        y, x = cellpos
        y %= CH
        x %= CW
        return x * CS + CS / 2, y * CS + CS / 2

    def drawcell(self, surface, pos, col, width=0):
        y, x = pos
        CS = self.CS
        x *= CS
        y *= CS
        pg.draw.rect(surface, col, [x, y, CS, CS], width)

    def drawcell2(self, surface, pos, col):
        pg.draw.circle(
            surface, col,
            self.toscreen(pos), self.CS / 3)

    def quit(self, *args):
        self.keep_running = False

    def screenshot(self, ev):
        # pdb.set_trace()
        surface = pg.display.get_surface()
        pim = stuff.pygame_to_pim(surface)
        stuff.pim_to_clipboard(pim)

    def keydown(self, ev):
        handler = self.keydown.handlerz.get(ev.key)
        if handler is not None:
            handler(self, ev)

    keydown.handlerz = {
        pg.K_ESCAPE: quit,
        pg.K_q: quit,
        pg.K_PRINTSCREEN: screenshot,
    }

    def mousemotion(self, ev):
        return
        # print(ev)
        # ipos = np.array([ev.pos[0], ev.pos[1], 1]) @ self.inv
        # print(ipos)
