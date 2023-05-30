import textwrap
from itertools import zip_longest


def build_column_layout(issues):
    # Define the maximum width for each column
    max_title_length = max(len(issues[i][0]) for i in range(len(issues)))
    padding = 15  # Adjust the padding as needed
    max_width = max_title_length + padding

    # Calculate the number of items in each column
    num_items = len(issues)
    half_num_items = (num_items + 1) // 2

    # Split the issues into two columns
    issues_left = issues[:half_num_items]
    issues_right = issues[half_num_items:]

    # Print the issues in two columns
    for index, (left, right) in enumerate(zip_longest(issues_left, issues_right), start=1):
        left_num = str(index)
        right_num = str(index + half_num_items)

        # Determine the padding based on the number of digits
        if len(left_num) == 1:
            left_num = f'  {left_num}.'
        elif len(left_num) == 2:
            left_num = f' {left_num}.'
        else:
            left_num = f'{left_num}.'

        if right is None:
            right_num = ''

        elif len(right_num) == 1:
            right_num = f'  {right_num}.'

        elif len(right_num) == 2:
            right_num = f' {right_num}.'

        else:
            right_num = f'{right_num}.'

        left_title = left[0] if left is not None else ''
        right_title = right[0] if right is not None else ''

        wrapped_left = textwrap.wrap(left_title, width=max_width - len(left_num) - 2)
        wrapped_right = textwrap.wrap(right_title, width=max_width - len(right_num) - 2)

        max_lines = max(len(wrapped_left), len(wrapped_right))

        for line_num in range(max_lines):
            line_left = wrapped_left[line_num] if line_num < len(wrapped_left) else ''
            line_right = wrapped_right[line_num] if line_num < len(wrapped_right) else ''

            print(f'{left_num} {line_left:<{max_width - len(left_num) - 2}} {right_num} {line_right}')
