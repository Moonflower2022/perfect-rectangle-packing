import numpy as np
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
from utils import (
    can_make_sum,
    count_unique_permutations,
    in_puzzle,
    puzzle_to_string
)
import sys
from sympy.utilities.iterables import multiset_permutations

def can_place(puzzle, size, position):
    # Early boundary check to avoid unnecessary slicing
    end_row = position[0] + size[0] - 1
    end_col = position[1] + size[1] - 1

    # Assuming puzzle_lengths is (rows, cols) of the puzzle
    if end_row >= puzzle.shape[0] or end_col >= puzzle.shape[1]:
        return False

    # Direct boolean check without np.any()
    # Use .view() to avoid copy, ravel() to flatten the view
    return (
        not puzzle[
            position[0] : position[0] + size[0], position[1] : position[1] + size[1]
        ]
        .view()
        .ravel()
        .any()
    )


def get_new_corners(
    new_puzzle_state, size, corner_to_place_on, current_corners, puzzle_lengths
):
    new_corners = current_corners[:]

    new_corners.remove(corner_to_place_on)

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

        x_border = new_puzzle_state[corner_y + size[0], corner_x : corner_x + size[1]]

        x_diagonal_indices = [corner_y + size[0], corner_x - 1]

        if all([border_element == 0 for border_element in x_border]):
            if (
                not in_puzzle(x_diagonal_indices, puzzle_lengths)
                or new_puzzle_state[x_diagonal_indices[0]][x_diagonal_indices[1]] != 0
            ):
                if in_puzzle((corner_y + size[0], corner_x), puzzle_lengths):
                    new_corners.append((corner_y + size[0], corner_x))
        else:
            first_non_zero_index = -1

            for i, border_element in enumerate(x_border):
                if first_non_zero_index != -1 and border_element == 0:
                    new_corners.append((corner_y + size[0], first_non_zero_index + 1))
                    break

                if border_element != 0 and first_non_zero_index == -1:
                    first_non_zero_index = i

    if corner_x + size[1] < puzzle_lengths[1]:
        y_border = new_puzzle_state[corner_y : corner_y + size[0], corner_x + size[1]]

        y_diagonal_indices = [corner_y - 1, corner_x + size[1]]

        if all([border_element == 0 for border_element in y_border]):
            if (
                not in_puzzle(y_diagonal_indices, puzzle_lengths)
                or new_puzzle_state[y_diagonal_indices[0]][y_diagonal_indices[1]] != 0
            ):
                if in_puzzle((corner_y, corner_x + size[1]), puzzle_lengths):
                    new_corners.append((corner_y, corner_x + size[1]))
        else:
            first_non_zero_index = -1

            for i, border_element in enumerate(y_border):
                if first_non_zero_index != -1 and border_element == 0:
                    new_corners.append((first_non_zero_index + 1, corner_x + size[1]))
                    break

                if border_element != 0 and first_non_zero_index == -1:
                    first_non_zero_index = i

    return new_corners


def check_state(puzzle, size, corner, remaining_pieces):
    corner_y, corner_x = corner

    if can_place(puzzle, size, corner):
        if corner_x + size[1] < len(puzzle[0]):
            x = corner_x + size[1] + 1
            while x < len(puzzle[1]) and puzzle[corner_y][x] == 0:
                x += 1

            if not can_make_sum(remaining_pieces, x - corner_x - size[1]):
                return False
        if corner_y + size[0] < len(puzzle):
            y = corner_y + size[0] + 1
            while y < len(puzzle) and puzzle[y][corner_x] == 0:
                y += 1

            if not can_make_sum(remaining_pieces, y - corner_y - size[0]):
                return False
    else:
        return False
    return True

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
        (corner_y, corner_x),
        corners,
        puzzle_lengths,
    )

    return new_puzzle_state, new_corners


def get_possible_next_states(
    puzzle, corners, piece_with_id_to_place, remaining_pieces, puzzle_lengths
):
    # puzzle is a np array of the size
    # corners is a list of current_corners, should be in ((corner_y, corner_x))
    # to_place is the next item to place, should be in (id, (dimension1, dimension2))

    # returns list of next states in the form of [(puzzle, corners)]

    possible_next_states = []

    id, size = piece_with_id_to_place

    for corner_y, corner_x in corners:
        if check_state(puzzle, size, (corner_y, corner_x), remaining_pieces):
            possible_next_states.append(
                get_next_state(
                    puzzle, corners, size, (corner_y, corner_x), id, puzzle_lengths
                )
            )
        if size[0] != size[1] and check_state(puzzle, size[::-1], (corner_y, corner_x), remaining_pieces):
            possible_next_states.append(
                get_next_state(
                    puzzle,
                    corners,
                    size[::-1],
                    (corner_y, corner_x),
                    id,
                    puzzle_lengths,
                )
            )

    return possible_next_states


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
            remaining_pieces.append(pieces_with_id[piece_order[current_index]][1])
            return (True, result[1])

    remaining_pieces.append(pieces_with_id[piece_order[current_index]][1])

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
            output_file.write(str(result[1]) + "\n\n")


def solve(puzzle_lengths, pieces_unique, indices, remaining_pieces):
    assert puzzle_lengths[0] * puzzle_lengths[1] == sum(
        [pieces_unique[i][0] * pieces_unique[i][1] for i in indices]
    )

    pieces_with_id = list(enumerate(pieces_unique, start=1))

    puzzle = np.zeros((puzzle_lengths[0], puzzle_lengths[1]), dtype=np.int16)
    corners = [(0, 0)]

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

    # for i, permutation in enumerate(unique_permutations(indices)):
    #     partial_process_permutation(permutation)
    #     if i > 300:
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
    else:
        raise Exception("resnt")

    solve(puzzle_lengths, pieces_unique, indices, remaining_pieces)
