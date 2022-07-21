import random as rnd
from collections import defaultdict, deque
from typing import Optional

import numpy as np
from tqdm import tqdm


def create_grid(rows: int, cols: int) -> list[list[str]]:
    grid = [
        ['_' for _ in range(cols)]
        for _ in range(rows)
    ]
    return grid


def visualize_dungeon(dungeon: list[list[str]]) -> None:
    for row in dungeon:
        print(row)


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

            grid[r][c] = 'X'

    grid[s_r][s_c] = 'O'
    return grid


def get_dungeon_stats(dungeon: list[list[str]]) -> dict[str, int]:
    stats = defaultdict(int)  # type: ignore
    for row in dungeon:
        for room in row:
            if room == '_':
                continue
            stats['rooms'] += 1

    return dict(stats)


def find_possible_boss_rooms(dungeon: list[list[str]]) -> list[tuple[int, int]]:
    rows, cols = len(dungeon), len(dungeon[0])
    possible_boss_rooms = []

    for r, row in enumerate(dungeon):
        for c, room in enumerate(row):
            if room != 'X':
                continue

            connections = 0

            for cr, cc in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
                if (0 < cr < rows) and (0 < cc < cols) and (dungeon[cr][cc] != '_'):
                    connections += 1

                if connections > 1:
                    break

            if connections == 1:
                possible_boss_rooms.append((r, c))

    return possible_boss_rooms


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
            if (0 <= x2 < rows) and (0 <= y2 < cols) and (grid[y2][x2] != '_') and ((x2, y2) not in seen):
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))

    return []


def get_boss_room(dungeon: list[list[str]], min_path_len: int) -> tuple[int, int]:
    boss_rooms = find_possible_boss_rooms(dungeon)

    boss_path_len = 0
    for br_corr in boss_rooms:
        shortest_path = find_shortest_path(dungeon, (rows // 2, cols // 2), br_corr)
        if len(shortest_path) > boss_path_len:
            boss_path_len = len(shortest_path)
            br_r, br_c = br_corr

    if boss_path_len < min_path_len:
        return -1, -1

    return br_r, br_c


if __name__ == "__main__":
    rows, cols = grid_size = (15, 15)

    while True:
        dungeon = dig_dungeon(rows, cols)
        rooms_num = get_dungeon_stats(dungeon)['rooms']
        if rooms_num < 16:
            continue

        br_r, br_c = get_boss_room(dungeon, 5)
        if (br_r, br_c) == (-1, -1):
            continue

        dungeon[br_r][br_c] = 'B'
        break

    visualize_dungeon(dungeon)

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
