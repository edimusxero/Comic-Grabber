import textwrap


def build_column_layout(issues):
    # Define the maximum width for each column
    max_width = 65

    # Calculate the number of items in each column
    num_items = len(issues)
    half_num_items = (num_items + 1) // 2

    # Split the issues into two equal halves
    issues_left = issues[:half_num_items]
    issues_right = issues[half_num_items:]

    # Calculate the maximum prefix length based on the number of items
    max_prefix_length = len(str(num_items))

    # Print the issues in two columns
    for index, (left, right) in enumerate(zip(issues_left, issues_right), start=1):
        left_num = str(index)
        right_num = str(index + half_num_items)

        # Determine the padding based on the number of digits
        if len(left_num) == 1:
            left_num = f'  {left_num}.'
        elif len(left_num) == 2:
            left_num = f' {left_num}.'
        else:
            left_num = f'{left_num}.'

        if len(right_num) == 1:
            right_num = f'  {right_num}.'
        elif len(right_num) == 2:
            right_num = f' {right_num}.'
        else:
            right_num = f'{right_num}.'

        left_title = left[0]
        right_title = right[0]

        wrapped_left = textwrap.wrap(left_title,
                                     width=max_width - max_prefix_length - 2)
        wrapped_right = textwrap.wrap(right_title,
                                      width=max_width - max_prefix_length - 2)

        for line_left, line_right in zip(wrapped_left, wrapped_right):
            print(f'{left_num} {line_left:<{max_width - max_prefix_length - 2}} {right_num} {line_right}')
