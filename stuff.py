import collections
import io
import math
import random

import pygame as pg
import win32clipboard
from PIL import Image

from maze.constants import DIRECTIONS, FieldValue


def maze_build(field):
    """
    field配列に迷路を構築する
    @return
        スタート, ゴール
    """
    h, w = field.shape
    field[:] = FieldValue.WALL

    pos = (random.randint(0, h - 3) | 1, random.randint(0, w - 3) | 1)
    maze_dig(field, pos)

    start, goal = random.sample([
        (0, 1), (h - 1, 1), (0, w - 2), (h - 1, w - 2),
    ], 2)

    field[start] = FieldValue.SPACE
    field[goal] = FieldValue.SPACE

    return start, goal


def maze_dig(field, pos):
    q = [pos]
    while q:
        pos = q.pop()
        candidate = digable(field, pos)
        if not candidate:
            continue
        y, x = pos
        while candidate:
            if len(candidate) > 1:
                q.append(pos)
            dy, dx = random.choice(candidate)
            y += dy
            x += dx
            field[y, x] = FieldValue.SPACE
            y += dy
            x += dx
            pos = (y, x)
            field[pos] = FieldValue.SPACE
            candidate = digable(field, pos)


def digable(field, pos):
    ls = []
    h, w = field.shape
    for dv in DIRECTIONS:
        y, x = (pos[0] + dv[0] * 2, pos[1] + dv[1] * 2)
        if y < 0 or x < 0 or y >= h or x >= w:
            continue
        if field[y, x] == FieldValue.WALL:
            ls.append(dv)
    return ls


def maze_solver(field, start, goal, depthfirst=False):
    h, w = field.shape
    field = field.copy()
    q = collections.deque()

    if depthfirst:
        def pop(): return q.pop()
    else:
        def pop(): return q.popleft()

    pos = goal
    while pos != start:
        for i, dv in enumerate(DIRECTIONS):
            tpos = (pos[0] + dv[0], pos[1] + dv[1])
            y, x = tpos
            if y < 0 or x < 0 or y >= h or x >= w:
                continue
            if field[tpos] == FieldValue.SPACE:
                field[tpos] = FieldValue.VISITED + i
                q.append(tpos)
        if not q:
            break
        pos = pop()

    pos = start
    yield pos
    while pos != goal:
        r = field[pos] - FieldValue.VISITED
        dv = DIRECTIONS[r]
        pos = (pos[0] - dv[0], pos[1] - dv[1])
        yield pos


def wiper(
        surf: pg.Surface,
        col: pg.Color,
        t: float,
        ndiv=32,
        virtical=True,
        reverse=False):
    width = surf.get_width()
    height = surf.get_height()

    if virtical:
        L = math.ceil(height / ndiv)

        def drawmask(i, h):
            y = L * i
            pg.draw.rect(surf, col, [0, y, width, h], 0)

    else:
        L = math.ceil(width / ndiv)

        def drawmask(i, w):
            x = L * i
            pg.draw.rect(surf, col, [x, 0, w, height], 0)

    if reverse:
        def f(i): return (1 + i) / ndiv
    else:
        def f(i): return (ndiv - i) / ndiv

    a = 1 / ndiv
    b = ndiv + 1
    c = b * t + a * (1 - t)
    Lc = L * c

    for i in range(ndiv):
        d = min(L, int(Lc * f(i)))
        drawmask(i, d)


def bezier(p0, p1, p2, p3, t):
    _t = 1 - t
    # まず、制御点を順に結んで得られる3つの線分
    # P0 - P1, P1 - P2, P2 - P3（緑色の線）をそれぞれ
    # t : 1 − t の比率で分割する点、P4, P5, P6 を求める。
    p4 = p0 * _t + p1 * t
    p5 = p1 * _t + p2 * t
    p6 = p2 * _t + p3 * t

    # 次に、これらの点を順に結んで得られる2つの線分
    # P4 - P5, P5 - P6（赤色の線）を再びそれぞれ
    # t : 1 − t の比率で分割する点 P7, P8 を求める。
    p7 = p4 * _t + p5 * t
    p8 = p5 * _t + p6 * t

    # 最後に、この2点を結ぶ線分 P7 - P8（黄色の線）をさらに
    # t : 1 − t の比率で分割する点 P9 を求めると、この点がベジェ曲線上の点となる。
    p9 = p7 * _t + p8 * t

    # この作業を 0 < t < 1 の範囲で繰り返し行う事により、P0, P1, P2, P3 を制御点とする3次ベジェ曲線（青い曲線）が得られる。
    return p9


def pim_to_clipboard(pim):
    with io.BytesIO() as output:
        pim.convert('RGB').save(output, 'BMP')
        data = output.getvalue()

    win32clipboard.OpenClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data[14:])
    win32clipboard.CloseClipboard()


def pygame_to_pim(surface):
    raw_str = pg.image.tostring(surface, 'RGBA', False)
    pim = Image.frombytes('RGBA', surface.get_size(), raw_str)
    return pim
