from utils import in_puzzle
import numpy as np

def get_bottom_corner1(puzzle, size, corner_to_place_on, puzzle_lengths):
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



def get_bottom_corner2(puzzle, size, corner_to_place_on, puzzle_lengths):
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

if __name__ == "__main__":
    puzzle_lengths = (3, 3)

    example_puzzle = np.zeros(puzzle_lengths)

    print(example_puzzle)

    inputs1 = [example_puzzle, (2, 2), (0, 0), puzzle_lengths]

    bottom_corner = get_bottom_corner1(*inputs1)
    print(get_bottom_corner1(*inputs1))
    print(get_bottom_corner2(*inputs1))
    assert get_bottom_corner1(*inputs1) == get_bottom_corner2(*inputs1)

    # example_puzzle[bottom_corner[0]][bottom_corner[1]] = 2

    # inputs2 = [example_puzzle, (2, 2), bottom_corner, puzzle_lengths]

    # print(get_bottom_corner1(*inputs2))
    # assert get_bottom_corner1(*inputs2) == get_bottom_corner2(*inputs2)