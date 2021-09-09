import argparse
import time

import pygame as pg

from .classes import Eventman, Taskman, World
from .constants import FieldValue
from .stuff import wiper
from .util import cubicbezier, hsv2rgb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--cellsize', type=int, default=16,
        help="specify cell px size")
    parser.add_argument(
        '-f', '--fullscreen',
        action="store_true", help="Fullscreen mode")
    args = parser.parse_args()

    pg.init()
    info = pg.display.Info()
    pg.display.set_caption("迷路")
    # pg.key.set_repeat(200, 20)
    w, h = info.current_w, info.current_h
    if not args.fullscreen:
        w, h = int(w * 0.7), int(h * 0.7)
    CS = args.cellsize
    CW, CH = w // CS, h // CS
    if CH & 1 == 0:
        CH -= 1
    if CW & 1 == 0:
        CW -= 1
    if not args.fullscreen:
        w, h = CS * CW, CS * CH
    pg.display.set_mode((w, h), pg.FULLSCREEN if args.fullscreen else 0)

    Eventman.broadcast("pygame ready")

    w = World(CS, (CH, CW))
    w.wipe = 0
    w.wipe_args = {}
    w.task = Taskman()
    w.task.add(maintask(w))
    clock = pg.time.Clock()
    surface = pg.display.get_surface()

    while w.keep_running:
        for event in pg.event.get():
            Eventman.broadcast(event.type, event)
        clock.tick(60)
        w.task.update()
        Eventman.broadcast("update")
        w.update_cellsurf()
        surface.blit(w.cellsurf, (0, 0))
        Eventman.broadcast("draw", surface)
        if w.wipe > 0:
            wiper(surface, (0, 0, 0), w.wipe, **w.wipe_args)
        pg.display.update()

    pg.quit()


def timer(duration):
    start = time.time()
    end = start + duration
    now = start
    while now < end:
        elapsed = now - start
        yield elapsed / duration
        now = time.time()
    yield 1


def maintask(world: World):
    ease = cubicbezier(1, 0, .39, 1)
    # ease = cubicbezier(0, 1, 1, 0)

    @Eventman.listener(pg.KEYDOWN)
    def keydown(ev):
        keydown.flag = not keydown.flag

    keydown.flag = True
    loopcount = 0

    while True:
        world.wipe_args["virtical"] = (loopcount & 4) != 0
        world.wipe_args["reverse"] = (loopcount & 2) != 0

        field, route, route2 = world.q.get()
        world.set_field(field)

        for t in timer(2):
            world.wipe = ease(1 - t)
            yield

        keydown.flag = True
        for pos in route:
            field[pos] = FieldValue.ROUTE
            if keydown.flag:
                yield

        keydown.flag = True
        for pos in set(route2) - set(route):
            field[pos] = FieldValue.ROUTE2
            if keydown.flag:
                yield

        @Eventman.listener("draw")
        def draw(surf):
            t = time.time()
            t -= int(t)
            for i, pos in enumerate(route2):
                h = i / 14 - t
                col = hsv2rgb(h, 1, 255)
                world.drawcell2(surf, pos, col)

        keydown.flag = False
        for t in timer(60):
            if keydown.flag:
                break
            yield

        for t in timer(2):
            world.wipe = ease(t)
            yield

        del draw
        loopcount += 1


if __name__ == "__main__":
    main()
