# Edison Puzzle Solver Comparison

This repository contains two implementations of a solver for the Edison Puzzle, a challenging rectangle packing problem. The implementations demonstrate significant performance differences through various optimization techniques. My goal was to improve upon and beat the original times clocked by Luigi Mangione's solving algorithm, which was achieved as I have clocked 34-39 ms solves on a sub-standard CPU.

## Problem Overview

The puzzle involves fitting 12 rectangular pieces into a 56x56 grid. Each piece can be rotated 90 degrees, and the goal is to find a valid arrangement where all pieces fit without overlapping.

<p align="center">
  <img src="https://www.creativeescaperooms.com/cdn/shop/files/calibron-12-solve-the-infamous-edison-puzzle-challenge-creative-crafthouse-995016.png?v=1749434638&width=800" alt="Calibron 12 Puzzle" width="800"/>
</p>



## Implementation Comparison

### Original Solver (`solver.py`)

The original implementation uses a straightforward backtracking approach with the following characteristics:

- Uses a 2D boolean array to represent the board
- Implements basic piece placement and rotation
- Uses simple backtracking without optimization
- Relies on Python's built-in list operations
- No caching or memoization

### Improved Solver (`improved_solver.py`)

The improved implementation achieves significantly better performance through several key optimizations:

#### 1. NumPy Integration
- Uses NumPy arrays instead of Python lists for board representation
- Leverages vectorized operations for faster piece placement and checking
- Reduces memory overhead and improves computation speed

#### 2. Caching and Memoization
- Implements `@lru_cache` for piece rotations
- Uses a transposition table to avoid revisiting states
- Caches board hashes and free positions
- Precomputes piece areas for faster calculations

#### 3. Optimized Search Strategy
- Sorts pieces by area (largest first) to reduce search space
- Implements early pruning when remaining pieces can't fill the space
- Uses efficient next-free position finding with NumPy operations

#### 4. Memory Management
- Implements proper hash and equality methods for the Board class
- Uses efficient copying mechanisms for board states
- Maintains caches for frequently accessed values

#### 5. State Tracking
- Tracks remaining area to enable early pruning
- Maintains piece rotation information
- Uses efficient position tracking for piece placement

## Performance Improvements

The improved solver achieves better performance through:

1. **Reduced Search Space**
   - Early pruning of impossible states
   - Sorted piece placement strategy
   - Transposition table to avoid redundant states

2. **Faster Operations**
   - Vectorized NumPy operations
   - Cached computations
   - Efficient state representation

3. **Memory Efficiency**
   - Optimized data structures
   - Better state management
   - Reduced copying overhead

## Key Code Differences

### Board Representation
```python
# Original
self.grid = [[True for _ in range(Board.SIZE)] for _ in range(Board.SIZE)]

# Improved
self.grid = np.ones((BOARD_SIZE, BOARD_SIZE), dtype=bool)
```

### Piece Fitting Check
```python
# Original
for w in range(piece[0]):
    for h in range(piece[1]):
        if not self.grid[self.next_free[1] + h][self.next_free[0] + w]:
            return False

# Improved
return np.all(self.grid[self.next_free[1]:self.next_free[1] + piece[1], 
                       self.next_free[0]:self.next_free[0] + piece[0]])
```

### State Management
```python
# Original
# No state caching or tracking

# Improved
@lru_cache(maxsize=1024)
def get_rotations(piece):
    w, h = piece
    if w == h:
        return (piece,)
    return (piece, (h, w))
```

## Conclusion
These optimizations make the improved solver much faster while maintaining the same, if not better solution quality. 
I've also attached a visualized version of my improved solver, though it is obviously slower due to rendering overhead and additional delays to allow the user to see the process. I've considered multithreading it but I think that the synchronization would add more overhead than it would reduce.