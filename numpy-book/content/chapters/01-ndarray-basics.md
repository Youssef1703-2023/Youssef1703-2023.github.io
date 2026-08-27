---
title: The ndarray — NumPy's Core Object
order: 1
source: "Sample lesson — JoeTech, NumPy Course, Video 1 (placeholder for design review)"
---

If you remember one idea from this lesson, make it this one: **NumPy exists because Python lists are slow for numerical work, and the ndarray is the object that fixes that.** A Python list can hold anything — an int, a string, another list — and Python pays for that flexibility by storing each element as a separate object scattered in memory. An ndarray gives that up on purpose: every element has the same type and sits in one continuous block of memory, which is what lets NumPy hand the actual math off to fast, compiled C code instead of looping in Python.

## What actually is an ndarray?

Think of an ndarray as three things bundled together: a block of raw memory, a **shape** that says how to read that memory as rows/columns/etc., and a **dtype** that says how many bytes each element takes and how to interpret them. Once you view it that way, a lot of "weird" NumPy behavior stops being weird — reshaping is just relabeling the same memory, and a slice is just a different way of walking over it.

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([[1, 2, 3], [4, 5, 6]])

print(a.shape)   # (3,)      -> 1 axis, 3 elements
print(b.shape)   # (2, 3)    -> 2 axes: 2 rows, 3 columns
print(b.dtype)   # int64     -> every element is a 64-bit integer
```

You rarely build arrays element by element. NumPy ships constructors for the shapes you need most often:

| Function | Produces |
|---|---|
| `np.zeros((r, c))` | array filled with `0.0` |
| `np.ones((r, c))` | array filled with `1.0` |
| `np.arange(start, stop, step)` | evenly spaced values, like `range()` |
| `np.linspace(start, stop, n)` | `n` evenly spaced values, inclusive of both ends |
| `np.eye(n)` | an `n x n` identity matrix |

<div class="box warn">
  <div class="box-label">Watch out</div>
  <p>A NumPy array's <code>dtype</code> is fixed at creation. Assign a float into an integer array and NumPy quietly truncates it instead of raising an error. Coming from plain Python lists, this is one of the easiest bugs to write without noticing:</p>
</div>

```python
ints = np.array([1, 2, 3])
ints[0] = 9.9
print(ints)   # [9 2 3]  -- silently truncated, no warning
```

## Shape, axes, and reshaping

Every ndarray carries a `.shape` tuple describing its size along each axis, and a `.ndim` telling you how many axes there are. `reshape()` does **not** copy data — it changes how the same underlying block of memory is *viewed*:

```python
c = np.arange(12)
grid = c.reshape(3, 4)

print(grid)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]

print(grid.T)            # transpose: swap the two axes
print(grid.flatten())    # back to 1-D, but this one *is* a copy
```

Because `reshape` hands back a view whenever it can, modifying `grid` after this point can also change `c` — they point at the same memory. This view-vs-copy distinction is the single idea that keeps coming back throughout the course: NumPy operations are fast largely *because* they avoid copying, so it always pays to know which ones share memory and which ones don't.

## Indexing and slicing

Indexing an ndarray reads like indexing a list, but it extends naturally to multiple dimensions with a comma inside the brackets instead of chained `[][]`:

```python
grid[0, 1]      # row 0, column 1        -> 1
grid[:, 0]      # every row, column 0    -> [0, 4, 8]
grid[1:, :2]    # rows 1 onward, first two columns
```

<div class="box">
  <div class="box-label">Tip</div>
  <p>A slice of an ndarray is a <span class="term">view</span>, not a copy — same rule as reshape. If you need an independent array, call <code>.copy()</code> explicitly: <code>sub = grid[1:, :2].copy()</code>.</p>
</div>

<div class="takeaways">
  <div class="box-label">Key takeaways</div>
  <ul>
    <li>An ndarray trades Python's per-element flexibility for one fixed <code>dtype</code> and one contiguous block of memory — that trade is the whole reason NumPy is fast.</li>
    <li><code>reshape()</code> and basic slicing return <strong>views</strong>, not copies. Two arrays can silently share the same underlying data.</li>
    <li>Assigning a value of the "wrong" type into an array truncates or converts it silently — there's no automatic error to catch this for you.</li>
    <li>Everything later in the course — broadcasting, vectorised math, aggregation along an axis — builds directly on <code>.shape</code>, <code>.dtype</code>, and this view/copy distinction.</li>
  </ul>
</div>
