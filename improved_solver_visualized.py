import copy
import time
import sys
import numpy as np
from functools import lru_cache
import visualizer
import pygame

# define board and pieces
BOARD_SIZE = 56
ALL_PIECES = [(28, 14), (21, 18), (21, 18), (21, 14), (21, 14), (32, 11), (32, 10), (28, 7), (28, 6), (17, 14), (14, 4), (10, 7)]

# precomp piece areas
PIECE_AREAS = {piece: piece[0] * piece[1] for piece in ALL_PIECES}

@lru_cache(maxsize=1024)
def get_rotations(piece):
    w, h = piece
    if w == h:
        return (piece,)
    return (piece, (h, w))

class Board:
    def __init__(self):
        self.grid = np.ones((BOARD_SIZE, BOARD_SIZE), dtype=bool)
        self.next_free = (0, 0)
        self.space = BOARD_SIZE * BOARD_SIZE
        self._next_free_cache = None
        self._hash = None
        self._free_positions = None

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((self.grid.tobytes(), self.next_free))
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, Board):
            return False
        return (self.grid == other.grid).all() and self.next_free == other.next_free

    def does_fit(self, piece):
        if self.next_free[0] + piece[0] > BOARD_SIZE or self.next_free[1] + piece[1] > BOARD_SIZE:
            return False
        return np.all(self.grid[self.next_free[1]:self.next_free[1] + piece[1], 
                               self.next_free[0]:self.next_free[0] + piece[0]])

    def find_next_free(self):
        """Find the next free position more efficiently"""
        if self._free_positions is None:
            # use numpy's optimized operations to find the first True value
            free_positions = np.where(self.grid)
            if len(free_positions[0]) > 0:
                self._free_positions = (int(free_positions[1][0]), int(free_positions[0][0]))
            else:
                self._free_positions = (BOARD_SIZE, BOARD_SIZE)
        return self._free_positions

    def insert(self, piece):
        position = self.next_free
        self.grid[self.next_free[1]:self.next_free[1] + piece[1], 
                 self.next_free[0]:self.next_free[0] + piece[0]] = False
        
        if self._next_free_cache is None:
            self.next_free = self.find_next_free()
        else:
            self.next_free = self._next_free_cache
            self._next_free_cache = None

        self.space -= piece[0] * piece[1]
        self._hash = None  # invalidate hash cache
        self._free_positions = None  # invalidate free positions cache
        return position

    def copy(self):
        copied_board = Board()
        copied_board.grid = self.grid.copy()
        copied_board.next_free = self.next_free
        copied_board.space = self.space
        return copied_board

def solve_puzzle():
    # init visualizer
    vis = visualizer.Visualizer()
    last_update_time = time.perf_counter()
    update_interval = 0.01  # Update visualization every 10ms
    
    # init timing metrics
    solve_start_time = time.perf_counter()
    visualization_time = 0
    last_vis_time = time.perf_counter()
    
    # sort pieces by area
    piece_sizes = [(i, PIECE_AREAS[piece]) for i, piece in enumerate(ALL_PIECES)]
    piece_sizes.sort(key=lambda x: x[1], reverse=True)
    sorted_pieces = [ALL_PIECES[idx] for idx, _ in piece_sizes]
    
    # precomp all rotations
    piece_rotations = {piece: get_rotations(piece) for piece in sorted_pieces}
    
    # transpos table to avoid revisited states
    transposition_table = {}
    
    def solve(board, remaining, positions, remaining_area):
        nonlocal last_update_time, visualization_time, last_vis_time
        
        # handle pygame events to keep window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # update visualization at fixed intervals
        current_time = time.perf_counter()
        if current_time - last_update_time >= update_interval:
            vis_start = time.perf_counter()
            vis.visualize(positions)
            visualization_time += time.perf_counter() - vis_start
            last_update_time = current_time

        # check transpos table
        board_hash = hash(board)
        if board_hash in transposition_table:
            return transposition_table[board_hash]
        
        if board.space == 0:
            return positions

        # early pruning: if remaining pieces can't fill the space
        if remaining_area < board.space:
            return None

        # try each piece
        for piece in remaining:
            # try each rotation
            for rot in piece_rotations[piece]:
                if board.does_fit(rot):
                    new_board = board.copy()
                    new_remaining = remaining.copy()
                    
                    # place the piece
                    position = new_board.insert(rot)
                    new_remaining.remove(piece)
                    positions.append((rot, position))
                    
                    # try to solve the rest
                    solution = solve(new_board, new_remaining, positions, remaining_area - PIECE_AREAS[piece])
                    if solution:
                        transposition_table[board_hash] = solution
                        return solution
                    
                    # backtrack
                    positions.pop()
        
        transposition_table[board_hash] = None
        return None

    # calc total area of remaining pieces
    total_area = sum(PIECE_AREAS[piece] for piece in sorted_pieces)
    
    # solve
    board = Board()
    solution = solve(board, sorted_pieces, [], total_area)
    
    # calc timing metrics
    total_time = time.perf_counter() - solve_start_time
    theoretical_time = total_time - visualization_time
    
    return solution, total_time, theoretical_time

if __name__ == "__main__":
    print("Starting improved_solver_visualized...")
    solution, total_time, theoretical_time = solve_puzzle()
    
    if solution:
        print(f"\nTiming Results:")
        print(f"Total time (with visualization): {total_time*1000:.1f} ms")
        print(f"Theoretical solve time (without visualization): {theoretical_time*1000:.1f} ms")
        print(f"Visualization overhead: {(total_time - theoretical_time)*1000:.1f} ms")
        print("\nSolution:")
        for rot, pos in solution:
            print(f"Piece {rot} at {pos}")
        
        # show final solution
        vis = visualizer.Visualizer()
        vis.visualize(solution)
        time.sleep(5)  # keep the final solution visible for 5 seconds
    else:
        print("No solution found")
    pygame.quit() 