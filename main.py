import argparse
import time

import pygame as pg

import maze.stuff as stuff
from maze.classes import Taskman, World
from maze.constants import FieldValue
from myutil import eventman
from myutil.cubicbezier import cubicbezier
from myutil.hsv2rgb import hsv2rgb


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

    eventman.broadcast("pygame ready")

    w = World(CS, (CH, CW))
    w.wipe = 0
    w.wipe_args = {}
    w.task = Taskman()
    w.task.add(maintask(w))
    clock = pg.time.Clock()
    surface = pg.display.get_surface()

    while w.keep_running:
        for event in pg.event.get():
            eventman.broadcast(event.type, event)
        clock.tick(60)
        w.task.update()
        eventman.broadcast("update")
        w.update_cellsurf()
        surface.blit(w.cellsurf, (0, 0))
        eventman.broadcast("draw", surface)
        if w.wipe > 0:
            stuff.wiper(surface, (0, 0, 0), w.wipe, **w.wipe_args)
        pg.display.update()

    pg.quit()


def maintask(world: World):
    ease = cubicbezier(1, 0, .39, 1)
    # ease = cubicbezier(0, 1, 1, 0)
    world.wipe_args["virtical"] = True
    world.wipe_args["reverse"] = False

    while True:
        field, route, route2 = world.q.get()
        world.set_field(field)

        end = time.time() + 2
        while time.time() < end:
            world.wipe = ease((end - time.time()) / 2)
            yield
        world.wipe = 0

        @eventman.listener(pg.KEYDOWN)
        def keydown(ev):
            keydown.flag = not keydown.flag

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

        @eventman.listener("draw")
        def draw(surf):
            t = time.time()
            t -= int(t)
            for i, pos in enumerate(route2):
                h = i / 14 - t
                col = hsv2rgb(h, 1, 255)
                world.drawcell2(surf, pos, col)

        end = time.time() + 60
        keydown.flag = True
        while time.time() < end and keydown.flag:
            yield

        world.wipe_args["reverse"] = not world.wipe_args["reverse"]
        end = time.time() + 2
        while time.time() < end:
            world.wipe = ease(1 - (end - time.time()) / 2)
            yield
        world.wipe = 1

        del draw, keydown
        world.wipe_args["virtical"] = not world.wipe_args["virtical"]


if __name__ == "__main__":
    main()