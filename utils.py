from collections import Counter
import math

# def test_get_new_corners():
#     example_puzzle = np.zeros((3, 3))
#     example_puzzle[0:2, 0:2] = 1
#     puzzle_lengths = [3, 3]

#     print(example_puzzle)

#     new_corners = get_new_corners(example_puzzle, (2, 2), (0, 0), [(0, 0)])

#     example_puzzle[new_corners[0][0]][new_corners[0][1]] = 2

#     print(get_new_corners(example_puzzle, (1, 1), new_corners[0], new_corners))


# def test_get_possible_next_states():
#     example_puzzle = np.zeros((3, 3))
#     example_puzzle[0:2, 0:2] = 1

#     print(example_puzzle)

#     new_corners = get_new_corners(example_puzzle, (2, 2), (0, 0), [(0, 0)])

#     print(new_corners)

#     print(get_possible_next_states(example_puzzle, new_corners, (2, (3, 1))))


def can_make_sum(tuples, target):
    """
    Ultra-fast check if target sum can be made using 1-5 values from different tuples.
    Returns only whether the sum is possible, not the values used.
    
    Args:
        tuples: List of tuples containing numbers
        target: Target sum to achieve
    
    Returns:
        bool: Whether the target sum is possible
    """
    # Convert tuples to sorted lists for faster access
    sorted_nums = [sorted(t) for t in tuples]
    max_tuples = min(5, len(tuples))
    
    # Pre-calculate bounds
    mins = [nums[0] for nums in sorted_nums]
    maxs = [nums[-1] for nums in sorted_nums]
    
    # Use set to store all possible sums
    possible_sums = {0}
    
    # Iterate through each tuple
    for i in range(len(sorted_nums)):
        # Early exit if we've found target
        if target in possible_sums:
            return True
            
        # Get all current sums that use fewer than 5 values
        current_sums = {s for s in possible_sums if s < target}
        
        # Add new sums using values from current tuple
        for value in sorted_nums[i]:
            for existing_sum in current_sums:
                new_sum = existing_sum + value
                if new_sum <= target:
                    possible_sums.add(new_sum)
    
    return target in possible_sums


def count_unique_permutations(array):
    """
    Calculate number of unique permutations without generating them.
    Uses the formula: n! / (n1! * n2! * ... * nk!)
    where n is total length and ni is count of each repeated element

    Args:
        lst: Input iterable that may contain duplicates

    Returns:
        Integer count of unique permutations
    """
    # Get count of each element
    counter = Counter(array)

    # Calculate numerator (n!)
    n = len(array)
    numerator = math.factorial(n)

    # Calculate denominator (product of factorials of counts)
    denominator = 1
    for count in counter.values():
        denominator *= math.factorial(count)

    return numerator // denominator


def unique_permutations(array):
    """
    Efficiently generate unique permutations of a list with duplicates.
    Uses a counting approach instead of sets for better performance.

    Args:
        array: Input iterable that may contain duplicates

    Yields:
        Tuples containing unique permutations
    """
    # Get count of each element
    counter = Counter(array)

    def _generate(current_perm, counter):
        # Base case: if current permutation is complete
        if len(current_perm) == len(array):
            yield tuple(current_perm)
            return

        # Try each unique element as the next item
        for num in counter:
            if counter[num] > 0:
                # Use this element
                counter[num] -= 1
                current_perm.append(num)

                # Recursively generate remaining permutations
                yield from _generate(current_perm, counter)

                # Backtrack
                current_perm.pop()
                counter[num] += 1

    yield from _generate([], counter)


def in_puzzle(indices, puzzle_lengths):
    return 0 <= indices[0] < puzzle_lengths[0] and 0 <= indices[1] < puzzle_lengths[1]

def puzzle_to_string(puzzle):
    string = ""
    for row in puzzle:
        for element in row:
            string += str(element) + " "
        string += "\n"
    return string

def flatten(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            # Recursively flatten the sub-list
            flat_list.extend(flatten(item))
        else:
            # Append the non-list item
            flat_list.append(item)
    return flat_list

if __name__ == "__main__":
    for i in range(100000):
        can_make_sum([(1, 2), (3, 4), (1, 2), (4, 5), (9, 0), (7, 1), (29, 38), (17, 10), (37, 6), (2, 6)], 29)
