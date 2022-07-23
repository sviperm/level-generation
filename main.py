import random as rnd
import sys
from collections import defaultdict, deque
from typing import Optional

import numpy as np
from tqdm import tqdm

max_int = sys.maxsize
min_int = -sys.maxsize - 1

ROOMS = {
    'empty': '.',
    'start': 'O',
    'room': 'X',
    'treasure': 'T',
    'boss': 'B',
    'secret': '?',
    # '2x2_tl': '┏',
    # '2x2_tr': '┓',
    # '2x2_bl': '┗',
    # '2x2_bl': '┛',
}


def create_grid(rows: int, cols: int) -> list[list[str]]:
    grid = [
        [ROOMS['empty'] for _ in range(cols)]
        for _ in range(rows)
    ]
    return grid


def visualize_dungeon(dungeon: list[list[str]]) -> None:
    for row in dungeon:
        for col in row:
            print(f' {col} ', end='')
        print()


def generate_direction(grid_size: tuple[int, int], r: int, c: int):
    directions = []
    rows, cols = grid_size

    if (r > 0):
        directions.append(0)
    if (c + 1 < cols):
        directions.append(1)
    if (r + 1 < rows):
        directions.append(2)
    if (c > 0):
        directions.append(3)

    return rnd.choice(directions)


def dig_dungeon(rows: int, cols: int, worms_num: Optional[int] = None) -> list[list[str]]:
    grid = create_grid(rows, cols)

    s_r, s_c = rows // 2, cols // 2

    if worms_num is None:
        worms_num = rnd.randrange(2, 5)

    worms_path = {
        2: (15, 20),
        3: (10, 15),
        4: (8, 12),
    }

    # worm initiation
    for _ in range(worms_num):
        r, c = s_r, s_c
        direction = None
        min_path, max_path = worms_path[worms_num]
        worm_path = rnd.randrange(min_path, max_path + 1)

        # worm digging
        for i in range(worm_path):
            direction = generate_direction((rows, cols), r, c)

            if direction == 0:
                r -= 1
            elif direction == 1:
                c += 1
            elif direction == 2:
                r += 1
            elif direction == 3:
                c -= 1

            grid[r][c] = ROOMS['room']

    grid[s_r][s_c] = ROOMS['start']
    return grid


def get_dungeon_stats(dungeon: list[list[str]]) -> dict[str, int]:
    stats = defaultdict(int)  # type: ignore
    for row in dungeon:
        for room in row:
            if room == ROOMS['empty']:
                continue
            stats['rooms'] += 1

    return dict(stats)


def get_end_rooms(dungeon: list[list[str]]) -> list[tuple[int, int]]:
    rows, cols = len(dungeon), len(dungeon[0])
    rooms = []

    for r, row in enumerate(dungeon):
        for c, room in enumerate(row):
            if room != ROOMS['room']:
                continue

            connections = 0

            for cr, cc in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
                if (0 <= cr < rows) and (0 <= cc < cols) and (dungeon[cr][cc] != ROOMS['empty']):
                    connections += 1

                if connections > 1:
                    break

            if connections == 1:
                rooms.append((r, c))

    return rooms


def get_secret_rooms(dungeon: list[list[str]]) -> dict[tuple[int, int], int]:
    rows, cols = len(dungeon), len(dungeon[0])
    rooms = {}

    for r, row in enumerate(dungeon):
        for c, room in enumerate(row):
            if room != ROOMS['empty']:
                continue

            connections = 0

            for cr, cc in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
                if (
                    (0 <= cr < rows) and
                    (0 <= cc < cols) and
                    (dungeon[cr][cc] != ROOMS['empty'])
                ):
                    if dungeon[cr][cc] == ROOMS['boss']:
                        connections = 0
                        break

                    connections += 1

            if connections > 1:
                rooms[(r, c)] = connections

    return rooms


def find_shortest_path(grid: list[list[str]], start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
    rows, cols = len(grid), len(grid[0])

    queue = deque([[start]])
    seen = set([start])

    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if (y, x) == goal:
            return [(y, x) for x, y in path]
        for x2, y2 in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (0 <= x2 < rows) and (0 <= y2 < cols) and (grid[y2][x2] != ROOMS['empty']) and ((x2, y2) not in seen):
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))

    return []


def get_boss_room(
    dungeon: list[list[str]],
    dead_ends_rooms: list[tuple[int, int]],
    min_path_len: int
) -> tuple[int, int]:
    rows, cols = len(dungeon), len(dungeon[0])

    boss_path_len = 0
    boss_room_index = 0
    for i, row_col in enumerate(dead_ends_rooms):
        shortest_path = find_shortest_path(dungeon, (rows // 2, cols // 2), row_col)
        if len(shortest_path) > boss_path_len:
            boss_path_len = len(shortest_path)
            boss_room_index = i

    if boss_path_len < min_path_len:
        return -1, -1

    boss_room_corr = dead_ends_rooms[boss_room_index]

    return boss_room_corr


# def find_pattern(dungeon: list[list[str]], pattern: list[list[str]]) -> list[tuple[int, int]]:
#     pass

def calc_min_max_rooms(level: float) -> tuple[int, int]:
    _min = level * 2
    _max = _min * 2
    temp = rnd.randint(1, 5) + 10
    return round(temp * _min), round(temp * _max)


def generate_dungeon(grid_size: tuple[int, int], seed: Optional[int] = None) -> list[list[str]]:
    if not seed:
        seed = rnd.randint(min_int, max_int)

    print(f'Seed: {seed}')
    rnd.seed(seed)

    rows, cols = grid_size
    # min_rooms, max_rooms = calc_min_max_rooms(level)

    while True:
        dungeon = dig_dungeon(rows, cols)
        rooms_num = get_dungeon_stats(dungeon)['rooms']
        if not (16 <= rooms_num <= 26):
            continue

        end_rooms = get_end_rooms(dungeon)
        if len(end_rooms) < 3:
            continue

        boss_r, boss_c = get_boss_room(dungeon, end_rooms, 5)
        if (boss_r, boss_c) == (-1, -1):
            continue
        dungeon[boss_r][boss_c] = ROOMS['boss']

        for r, c in end_rooms:
            if (r, c) != (boss_r, boss_c):
                dungeon[r][c] = ROOMS['treasure']

        secret_rooms = get_secret_rooms(dungeon)
        if not secret_rooms:
            continue

        is_secret_room = False
        for (r, c), con in secret_rooms.items():
            prob = rnd.random()
            treshold = {
                2: 0.25,
                3: 0.65,
                4: 0.9,
            }

            if prob <= treshold[con]:
                dungeon[r][c] = ROOMS['secret']
                is_secret_room = True

        if not is_secret_room:
            r, c = rnd.choice(list(secret_rooms.keys()))
            dungeon[r][c] = ROOMS['secret']

        return dungeon


if __name__ == "__main__":
    # level = 1
    grid_size = (15, 15)
    seed = None
    # seed = -8084925685050141357

    for _ in range(15):
        dungeon = generate_dungeon(grid_size, seed)
        visualize_dungeon(dungeon)

    # for l in [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5]:
    #     _min, _max = zip(*[calc_min_max_rooms(l) for _ in range(1000)])
    #     print(f'Level: {l}')
    #     for p in [5, 10, 25, 50, 75, 90, 95]:
    #         print(f'{p}%\tMin: {np.percentile(_min, p)}\tMax: {np.percentile(_max, p)}')
    #     print()

    #     paths.append(boss_path)

    # print('Boss path')
    # for p in [5, 10, 25, 50, 75, 90, 95]:
    #     print(f'{p}% {np.percentile(paths, p)}')
    # print('---------')

    # visualize_dungeon(dungeon)
    # print()
    # visualize_dungeon(bosses)

    # rooms: dict[int, list[int]] = {
    #     2: [],
    #     3: [],
    #     4: [],
    # }

    # iters = 1000
    # for _ in tqdm(range(iters), total=iters):
    #     for i in range(2, 5):
    #         dungeon = dig_dungeon(grid)
    #         rooms_num = get_dungeon_stats(dungeon)['rooms']
    #         rooms[i].append(rooms_num)

    # for k, v in rooms.items():
    #     print(f'Worms: {k}')
    #     for p in [5, 10, 25, 50, 75, 90, 95]:
    #         print(f'{p}% {np.percentile(v, p)}')
    #     print('---------')
