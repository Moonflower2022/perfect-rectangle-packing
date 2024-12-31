import re
import sys

def add_profile_decorator(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    # Add @profile to all function definitions
    profiled_code = re.sub(r'(?m)^def ', '@profile\ndef ', code)

    # Save to a new file or overwrite
    with open(file_path.replace('.py', '_profiled.py'), 'w') as file:
        file.write(profiled_code)

    print("Profiled code saved to:", file_path.replace('.py', '_profiled.py'))

# Example usage
add_profile_decorator('lowest_corner.py' if len(sys.argv) != 2 else sys.argv[1])