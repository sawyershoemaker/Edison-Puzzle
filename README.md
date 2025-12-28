# Edison Puzzle Solver Comparison

This repository contains two implementations of a solver for the Edison Puzzle, a challenging rectangle packing problem. The implementations demonstrate significant performance differences through various optimization techniques. My goal was to improve upon and beat the original times clocked by Luigi Mangione's solving algorithm, which was achieved as I have clocked ~10 ms solves on a sub-standard CPU.

## Problem Overview

The puzzle involves fitting 12 rectangular pieces into a 56x56 grid. Each piece can be rotated 90 degrees, and the goal is to find a valid arrangement where all pieces fit without overlapping.

<p align="center">
  <img src="https://www.creativeescaperooms.com/cdn/shop/files/calibron-12-solve-the-infamous-edison-puzzle-challenge-creative-crafthouse-995016.png?v=1749434638&width=800" alt="Calibron 12 Puzzle" width="800"/>
</p>

~~I've also attached a visualized version of my improved solver, though it is obviously slower due to rendering overhead and additional delays to allow the user to see the process. I've considered multithreading it but I think that the synchronization would add more overhead than it would reduce.~~ I CBA to hook the visualizer up to my new solution.

