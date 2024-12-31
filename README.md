# perfect-rectangle-packing

Repo with versions of a search algorithm for finding the way to fit all of a given list of rectangles that can be rotated by 90 degrees into a given bounding box.

# files

* `add_profile_decorator.py`: a script partly written by ChatGPT to take a script and add the `@profile` decorator to every function in a file (for using the `line-profiler` package)
* `brute_force.py`: my first attempt at this problem. DISCLAIMER: could have bugs. is not meant to be a slower version of `lowest_corner.py`
* `lowest_corner.py`: my latest solution to the problem, finds solution to Calibron 12 in about 2-3 hours
* `testing.py`: testing file for `get_bottom_corner` function
* `utils.py`: utility functions used across my files

# usage

* download the repo
* cd into the folder
* go into `lowest_corner.py` and change one of the modes to your puzzle
* run `python lowest_corner.py {whatever mode you used}`

for example, I could change
```py
    elif mode == "test3":
        puzzle_lengths = [3, 3]

        pieces_unique = [(3, 2), (3, 1)]
        remaining_pieces = pieces_unique
        indices = [0, 1]
```
to
```py
    elif mode == "test3":
        puzzle_lengths = [4, 4]

        pieces_unique = [(2, 2), (3, 1), (4, 1), (1, 1)]
        remaining_pieces = [(2, 2), (2, 2), (3, 1), (4, 1), (1, 1)]
        indices = [0, 0, 1, 2, 3] # these are for referencing `pieces_unique`, the double 0 indicates that there should be 2 of (2, 2)
```
and run `python lowest_corner.py test3`

# process of creation

This idea was started when my friend made me a Calibron 12 puzzle for my birthday. I've seen it before, but I have never been able to solve it. Thus, I wanted to write a program to solve it for me. 

I started by doing some research.
* <http://www.or.uni-bonn.de/~hougardy/paper/PerfectPacking.pdf>
* <https://www.csc.liv.ac.uk/~epa/surveyhtml.html#top>
* <https://www.codeproject.com/Articles/210979/Fast-optimizing-rectangle-packing-algorithm-for-bu?scrlybrkr=7aea1319#basic>
* <https://www.codeproject.com/Articles/5373703/Rectangle-Packing>
* <https://people.csail.mit.edu/rivest/pubs/pubs/BCR80.pdf>
* <https://eniacization.github.io/2017/12/28/backtracking-puzzle.html>
* <https://cdn.aaai.org/ICAPS/2003/ICAPS03-029.pdf>
* <https://www.david-colson.com/2020/03/10/exploring-rect-packing.html>
* <https://github.com/PhoenixSmaug/PerfectPacking.jl>
* <https://www.ijcai.org/Proceedings/09/Papers/092.pdf>
* <https://arxiv.org/pdf/1402.0557>

My first attempt was: for each unique ordering of the pieces, check if that ordering can fit in the box by placing pieces subsequently in top-left corners, accounting for rotation. It looked a little something like this (its full implementation can be found in `brute_force.py`):
```py
def get_new_states(board, corners, piece_to_place):
    new_states = []

    for corner in corners:
        if can_place(board, corner, piece_to_place):
            new_states.append(get_next_state(board, corner, piece_to_place))
        if piece_to_place[0] != piece_to_place[1] and can_place(board, corner, piece_to_place[::-1]):
            new_states.append(get_next_state(board, corner, piece_to_place[::-1]))

    return new_states

def can_fill(board, corners, piece_order, current_index):
    if current_index == len(piece_order):
        return True

    new_states = get_new_states(board, corners, piece_order[current_index])

    for new_board, new_corners in new_states:
        if can_fill(new_board, new_corners, piece_order, current_index + 1):
            return True

    return False
```

This was incredibly slow for my purposes, since Calibron 12 is a puzzle with 12 pieces and only 2 pieces that have one duplicate. This means there would be 12! / 2 / 2 = 119,750,400 piece orderings I would have to consider. Even after some optimization, my rate of completion was 166 orderings per second. Using this algorithm, it would take me 200 hours to finish the search.

After reaching this roadblock, I researched some more possible restructuring optimizations. I came across two resources that were very insightful:
* 2.2.2 Place in <https://leenderthofste.com/assets/pdf/Rectangle_Packing_Algorithms.pdf>
* Pruning rules in <http://www.or.uni-bonn.de/~hougardy/paper/PerfectPacking.pdf>

2.2.2 Place proposed only considering the lowest y-value corner when generating new states. This made sense, as since we are considering all orderings, considering all corners as well is redundant. After seeing other algorithms implement pruning rules for speed, I also decided to try it, and wrote a minimal one that pruned whenever after placing a rectagle, the length from its right edge to the right wall was not tilable, or if the left from its bottom edge to the bottom wall was not tilable. 

After doing a lot of profiling and optimizations, I found that my pruning strategy was actually making the program run slower (;-;), so I removed it. 

The final version (`lowest_corner.py`) has a rewritten `get_bottom_corner` function, selects only the lowest y-value corner when generating new states, and fixes a lot of bugs that (might) be present in `brute_force.py`. 

# future improvements

I have a couple of ideas for improvements to the algorithm:
* speedup
  * since many of the solutions right now are duplicates, maybe we could cache results of `can_fill` by hashing the numpy 2d array
  * maybe rewrite in a more low level lang
* qol
  * only show unique solutions
  * when showing solutions, somehow signify the difference between the identical pieces (right now they just have the same number)
  * maybe show them more graphically, since right now if there are 10 or more pieces, the visualization is not great