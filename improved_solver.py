import time
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

BOARD_SIZE = 56
FULL_ROW_MASK = (1 << BOARD_SIZE) - 1
USE_TRANSPOSITION = False

ALL_PIECES: Sequence[Tuple[int, int]] = (
    (28, 14),
    (21, 18),
    (21, 18),
    (21, 14),
    (21, 14),
    (32, 11),
    (32, 10),
    (28, 7),
    (28, 6),
    (17, 14),
    (14, 4),
    (10, 7),
)


@dataclass(frozen=True)
class Rotation:
    width: int
    height: int
    area: int
    row_mask: int


@dataclass(frozen=True)
class Piece:
    dims: Tuple[int, int]
    area: int
    rotations: Tuple[Rotation, ...]


def build_piece_library() -> Tuple[List[Piece], List[int]]:
    counter = Counter(ALL_PIECES)

    def rotation_variants(dim: Tuple[int, int]) -> Tuple[Rotation, ...]:
        w, h = dim
        area = w * h
        row_mask = (1 << w) - 1
        if w == h:
            return (Rotation(w, h, area, row_mask),)
        return (
            Rotation(w, h, area, row_mask),
            Rotation(h, w, area, (1 << h) - 1),
        )

    pieces = []
    counts = []
    # sort by area desc, then by max dimension to place awkward rectangles earlier
    for dims, count in sorted(
        counter.items(),
        key=lambda item: (item[0][0] * item[0][1], max(item[0]), min(item[0])),
        reverse=True,
    ):
        pieces.append(
            Piece(
                dims=dims,
                area=dims[0] * dims[1],
                rotations=rotation_variants(dims),
            )
        )
        counts.append(count)
    return pieces, counts


PIECES, INITIAL_COUNTS = build_piece_library()
TOTAL_PIECE_AREA = sum(piece.area * count for piece, count in zip(PIECES, INITIAL_COUNTS))


def find_first_free(rows: Sequence[int]) -> Optional[Tuple[int, int]]:
    for y, row in enumerate(rows):
        if row:
            lowest_bit = row & -row
            x = lowest_bit.bit_length() - 1
            return y, x
    return None


def solve_fast() -> Optional[List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
    size = BOARD_SIZE
    full_mask = FULL_ROW_MASK
    board_rows: List[int] = [full_mask for _ in range(size)]
    remaining_counts: List[int] = INITIAL_COUNTS.copy()
    placements: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
    transposition: Optional[dict[Tuple[Tuple[int, ...], Tuple[int, ...]], bool]] = (
        {} if USE_TRANSPOSITION else None
    )

    def search(remaining_area: int) -> bool:
        if remaining_area == 0:
            return True

        first_free = find_first_free(board_rows)
        if first_free is None:
            return False
        anchor_y, anchor_x = first_free

        state_key: Optional[Tuple[Tuple[int, ...], Tuple[int, ...]]] = None

        if transposition:
            state_key = (tuple(board_rows), tuple(remaining_counts))
            cached = transposition.get(state_key)
            if cached is False:
                return False

        for idx, count in enumerate(remaining_counts):
            if count == 0:
                continue
            piece = PIECES[idx]

            for rotation in piece.rotations:
                w, h = rotation.width, rotation.height
                end_x = anchor_x + w
                end_y = anchor_y + h
                if end_x > size or end_y > size:
                    continue

                mask = rotation.row_mask << anchor_x
                fits = True
                for row in range(anchor_y, end_y):
                    if board_rows[row] & mask != mask:
                        fits = False
                        break

                if not fits:
                    continue

                clear_mask = full_mask ^ mask
                for row in range(anchor_y, end_y):
                    board_rows[row] &= clear_mask

                placements.append(((rotation.width, rotation.height), (anchor_x, anchor_y)))
                remaining_counts[idx] -= 1

                if search(remaining_area - rotation.area):
                    return True

                remaining_counts[idx] += 1
                placements.pop()
                for row in range(anchor_y, end_y):
                    board_rows[row] |= mask

        if transposition is not None:
            if state_key is None:
                state_key = (tuple(board_rows), tuple(remaining_counts))
            transposition[state_key] = False

            if len(transposition) > 500_000:
                transposition.clear()

        return False

    success = search(TOTAL_PIECE_AREA)
    if success:
        return placements.copy()
    return None


def benchmark(iterations: int = 5) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        solve_fast()
    end = time.perf_counter()
    return (end - start) / iterations


if __name__ == "__main__":
    print("Running solver_fast...")
    t0 = time.perf_counter()
    solution = solve_fast()
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000.0

    if solution:
        print(f"Solution found in {elapsed_ms:.5f} ms")
        for dims, pos in solution:
            print(f"Piece {dims} at {pos}")
    else:
        print("No solution found.")

