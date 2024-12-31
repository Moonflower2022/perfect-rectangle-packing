import numpy as np
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
from utils import (
    can_make_sum,
    count_unique_permutations,
    in_puzzle,
    puzzle_to_string,
    flatten,
)
import sys
from sympy.utilities.iterables import multiset_permutations


def can_place(puzzle, size, position):
    # Early boundary check to avoid unnecessary slicing
    end_row = position[0] + size[0]
    end_col = position[1] + size[1]

    # Assuming puzzle_lengths is (rows, cols) of the puzzle
    if end_row > puzzle.shape[0] or end_col > puzzle.shape[1]:
        return False

    slice = puzzle[position[0] : end_row, position[1] : end_col]
    return not slice.any()


def get_bottom_corner(puzzle, size, corner_to_place_on, puzzle_lengths):
    corner_y, corner_x = corner_to_place_on

    # here, we should iterate through x values to see where the new corner should be
    # same for y values
    # cases (for x) let border_values = [puzzle[corner_y + size[0] + 1][x] for x in range(0, corner_x + size[1])]:
    # 1. all border_values is 0 --> no corner
    # 2. the non 0 values in border_values is just are all for x < corner_x --> no corner
    # 3. border_values has non 0 until some x in [corner_x, corner_x + size[1]] where it starts always being 0 --> corner at (corner_y + size[0], x)
    # 4. border_values is all non 0 --> no corner

    # this (case for x) can possibly be reduced to a check on the bottom left corner's immediate diagonal pixel (like (corner_y + size[0] + 1, corner_x - 1))
    # and the x values from corner_x to corner_x + size[1]
    if corner_y + size[0] < puzzle_lengths[0]:

        x_border = puzzle[corner_y + size[0], corner_x : corner_x + size[1]]

        x_diagonal_indices = [corner_y + size[0], corner_x - 1]

        if all([border_element == 0 for border_element in x_border]):
            if (
                not in_puzzle(x_diagonal_indices, puzzle_lengths)
                or puzzle[x_diagonal_indices[0]][x_diagonal_indices[1]] != 0
            ):
                if in_puzzle((corner_y + size[0], corner_x), puzzle_lengths):
                    return (corner_y + size[0], corner_x)
        else:
            first_non_zero_index = -1

            for i, border_element in enumerate(x_border):
                if first_non_zero_index != -1 and border_element == 0:
                    return (corner_y + size[0], first_non_zero_index + 1)

                if border_element != 0 and first_non_zero_index == -1:
                    first_non_zero_index = i
    return False



def get_bottom_corner(puzzle, size, corner_to_place_on, puzzle_lengths):
    corner_y, corner_x = corner_to_place_on

    # different (possibly faster approach):
    # iterate through list of x_border
    # first element that is [(not out of the game) and (not nonzero)] is the x value of the corner
    #

    if corner_y + size[0] < puzzle_lengths[0]:
        # x_border is y = corner_y + size[0], x = corner_x : corner_x + size[1]

        x_border = puzzle[corner_y + size[0], corner_x : corner_x + size[1]]

        x_diagonal_indices = [corner_y + size[0], corner_x - 1]

        left_most_zero_x = -1

        for x_offset, element in enumerate(x_border):
            x = corner_x + x_offset
            if element == 0:
                left_most_zero_x = x
                break

        if left_most_zero_x > corner_x:
            return (corner_y + size[0], left_most_zero_x)
        elif left_most_zero_x == corner_x:
            if (
                not in_puzzle(x_diagonal_indices, puzzle_lengths)
                or puzzle[x_diagonal_indices[0], x_diagonal_indices[1]] != 0
            ):
                return (corner_y + size[0], corner_x)

    return False

def get_new_corners(
    new_puzzle_state, size, corner_to_place_on, current_corners, puzzle_lengths
):
    new_corners = current_corners.copy()

    new_corners.discard(corner_to_place_on)

    bottom_corner = get_bottom_corner(
        new_puzzle_state, size, corner_to_place_on, puzzle_lengths
    )
    if bottom_corner:
        new_corners.add(bottom_corner)

    right_corner = get_bottom_corner(
        new_puzzle_state.T, size[::-1], corner_to_place_on[::-1], puzzle_lengths[::-1]
    )
    if right_corner:
        new_corners.add(right_corner[::-1])

    return new_corners


def check_state(puzzle, size, corner, remaining_pieces):
    return can_place(puzzle, size, corner)
    # corner_y, corner_x = corner

    # if can_place(puzzle, size, corner):
    #     if corner_x + size[1] < len(puzzle[0]):
    #         x = corner_x + size[1] + 1
    #         while x < len(puzzle[1]) and puzzle[corner_y][x] == 0:
    #             x += 1

    #         if not can_make_sum(remaining_pieces, x - corner_x - size[1]):
    #             return False
    #     if corner_y + size[0] < len(puzzle):
    #         y = corner_y + size[0] + 1
    #         while y < len(puzzle) and puzzle[y][corner_x] == 0:
    #             y += 1

    #         if not can_make_sum(remaining_pieces, y - corner_y - size[0]):
    #             return False
    #     pass
    # else:
    #     return False
    # return True


def get_next_state(puzzle, corners, size, corner, id, puzzle_lengths):
    corner_y, corner_x = corner

    new_puzzle_state = puzzle.copy()
    new_puzzle_state[
        corner_y : corner_y + size[0],
        corner_x : corner_x + size[1],
    ] = id

    new_corners = get_new_corners(
        new_puzzle_state,
        size,
        corner,
        corners,
        puzzle_lengths,
    )

    return new_puzzle_state, new_corners


def get_possible_next_states(
    puzzle, corners, piece_with_id_to_place, remaining_pieces, puzzle_lengths
):
    # puzzle is a np array of the size
    # corners is a list of current_corners, should be in (corner)
    # to_place is the next item to place, should be in (id, (dimension1, dimension2))

    # returns list of next states in the form of [(puzzle, corners)]

    id, size = piece_with_id_to_place

    lowest_corner_y = float("inf")
    lowest_corner_y_next_states = []

    for corner in corners:
        possible_next_states = []
        corner_is_possible = False

        if check_state(puzzle, size, corner, remaining_pieces):
            corner_is_possible = True
            possible_next_states.append(
                get_next_state(puzzle, corners, size, corner, id, puzzle_lengths)
            )
        if size[0] != size[1] and check_state(
            puzzle, size[::-1], corner, remaining_pieces
        ):
            corner_is_possible = True
            possible_next_states.append(
                get_next_state(
                    puzzle,
                    corners,
                    size[::-1],
                    corner,
                    id,
                    puzzle_lengths,
                )
            )

        if corner_is_possible and corner[0] < lowest_corner_y:
            lowest_corner_y = corner[0]
            lowest_corner_y_next_states = possible_next_states

    return lowest_corner_y_next_states


def can_fill(
    piece_order,
    puzzle,
    corners,
    current_index,
    pieces_with_id,
    remaining_pieces,
    puzzle_lengths,
):
    if current_index >= len(piece_order):
        return (True, puzzle)

    remaining_pieces.remove(pieces_with_id[piece_order[current_index]][1])

    possible_next_states = get_possible_next_states(
        puzzle,
        corners,
        pieces_with_id[piece_order[current_index]],
        remaining_pieces,
        puzzle_lengths,
    )

    solutions = []

    for new_puzzle_state, new_corners in possible_next_states:
        result = can_fill(
            piece_order,
            new_puzzle_state,
            new_corners,
            current_index + 1,
            pieces_with_id,
            remaining_pieces,
            puzzle_lengths,
        )
        if result[0]:
            solutions.append(result[1])

    remaining_pieces.append(pieces_with_id[piece_order[current_index]][1])
    if len(solutions) != 0:
        return (True, solutions)

    return (False, None)


def process_permutation(
    permutation, puzzle, corners, pieces_with_id, remaining_pieces, puzzle_lengths
):
    result = can_fill(
        permutation,
        puzzle,
        corners,
        0,
        pieces_with_id,
        remaining_pieces,
        puzzle_lengths,
    )

    if result[0]:
        with open("solution.txt", "a") as output_file:
            for solution in flatten(result[1]):
                output_file.write(puzzle_to_string(solution) + "\n")


def solve(puzzle_lengths, pieces_unique, indices, remaining_pieces):
    assert puzzle_lengths[0] * puzzle_lengths[1] == sum(
        [pieces_unique[i][0] * pieces_unique[i][1] for i in indices]
    )

    pieces_with_id = list(enumerate(pieces_unique, start=1))

    puzzle = np.zeros((puzzle_lengths[0], puzzle_lengths[1]), dtype=np.int16)
    corners = {(0, 0)}

    partial_process_permutation = partial(
        process_permutation,
        puzzle=puzzle,
        corners=corners,
        pieces_with_id=pieces_with_id,
        remaining_pieces=remaining_pieces,
        puzzle_lengths=puzzle_lengths,
    )

    with mp.Pool(mp.cpu_count()) as pool:
        list(
            tqdm(
                pool.imap(partial_process_permutation, multiset_permutations(indices)),
                total=count_unique_permutations(indices),
            )
        )

    # for i, permutation in enumerate(multiset_permutations(indices)):
    #     partial_process_permutation(permutation)
    #     if i > 1000:
    #         break


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "run":
        puzzle_lengths = [56, 56]
        pieces_unique = [
            (21, 18),
            (21, 14),
            (32, 11),
            (32, 10),
            (17, 14),
            (14, 4),
            (28, 7),
            (28, 14),
            (10, 7),
            (28, 6),
        ]
        indices = list(range(len(pieces_unique))) + [0, 1]
        remaining_pieces = pieces_unique + [(21, 18), (21, 14)]
    elif mode == "test":
        puzzle_lengths = [4, 3]
        # @5*
        # @5*
        # @!!
        # @!!

        # (y, x), id [but y and x are interchangeable]
        # id should be number
        pieces_unique = [(4, 1), (2, 2), (2, 1)]
        remaining_pieces = [(4, 1), (2, 2), (2, 1), (2, 1)]
        indices = [0, 1, 2, 2]
    elif mode == "test2":
        puzzle_lengths = [4, 3]

        pieces_unique = [(3, 2), (2, 2), (2, 1)]
        remaining_pieces = pieces_unique
        indices = [0, 1, 2]
    elif mode == "test3":
        puzzle_lengths = [3, 3]

        pieces_unique = [(3, 2), (3, 1)]
        remaining_pieces = pieces_unique
        indices = [0, 1]
    else:
        raise Exception("resnt")

    # piece_order = [pair[0] for pair in sorted(zip(indices, remaining_pieces), key=lambda pair: pair[1][0] * pair[1][1], reverse=True)]

    # print(piece_order)

    # puzzle = np.zeros(puzzle_lengths, dtype=np.int16)
    # corners = [(0, 0)]

    # print(can_fill(piece_order, puzzle, corners, 0, list(enumerate(pieces_unique)), remaining_pieces, puzzle_lengths))

    solve(puzzle_lengths, pieces_unique, indices, remaining_pieces)
