assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """


    for unit in unitlist:
        #For each unit, find all the unsolved boxes
        unsolved_box = [box for box in unit if len(values[box])>1]
        count={}
        twins_value=[]
        
        #Count the number of boxes with same value using a dictionary called count, 
        #count.keys() is the box value, count.values() is the number of box with that value
        #If len(value) == number of these boxes, they must be naked twins
        #Here not only boxes with len(value)==2 being considered, 
        #say if there are 3 boxes with the same value 127, then they are also 'twins'
        for box in unsolved_box:
            count[values[box]] = count.get(values[box],0)+1
            if len(values[box]) == count[values[box]]:
                twins_value.append(values[box])
                
        #If we find naked_twins in any unit, 
        #remove all digits contained in the naked_twins from all other unsolved boxes in the same unit
        for twins in twins_value:
            for box in unsolved_box:
                if values[box] != twins:
                    for digit in twins:
                        if digit in values[box]:
                            ind = values[box].index(digit)
                            values = assign_value(values, box, values[box][:ind]+values[box][ind+1:])
    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(row, cols) for row in rows]
col_units = [cross(rows, col) for col in cols]
square_units = [cross(row, col) for row in ['ABC', 'DEF', 'GHI'] for col in ['123','456','789']]
diagonal_units= [ [r+cols[ind] for ind, r in enumerate(rows)], [r+cols[-ind-1] for ind, r in enumerate(rows)] ]
unitlist = row_units + col_units + square_units + diagonal_units
units = dict((s,[unit for unit in unitlist if s in unit]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    for element in grid:
        if element.isdigit():
            chars.append(element)
        elif element == '.':
            chars.append('123456789')
        else:
            print('wrong input')
    assert len(chars) == 81
    return dict(zip(boxes,chars))



def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Args:
        values(dict): The sudoku in dictionary form
    Returns: 
        The resulting sudoku in dictionary form.
    """
    solved_boxes = [box for box in boxes if len(values[box])==1]
    for box in solved_boxes:
        value = values[box]
        for peer in peers[box]:
            if value in values[peer]:
                ind = values[peer].index(value)
                values = assign_value(values, peer, values[peer][:ind]+values[peer][ind+1:])
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Args:
        values(dict): The sudoku in dictionary form
    Returns: 
        The resulting sudoku in dictionary form.
    """
    
    for unit in unitlist:
        for num in '123456789':
            only_box = [box for box in unit if num in values[box]]
            if len(only_box) == 1:
                values = assign_value(values, only_box[0], num)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Args:
        values(dict): The sudoku in dictionary form
    Returns: 
        The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        solve_before = len([box for box in boxes if len(values[box])==1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solve_after = len([box for box in boxes if len(values[box])==1])
        stalled = ( solve_before == solve_after )
        if len([box for box in boxes if len(values[box])==0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    Args:
        values(dict): The sudoku in dictionary form
    Returns: 
        The resulting sudoku in dictionary form.
    """
    
    # Solve the puzzle using the reduce_puzzle() function
    values = reduce_puzzle(values)
    if not values:
        return False
    if all(len(values[box])==1 for box in boxes):
        return values
    
    # Choose one of the unsolved boxes with the fewest possibilities
    length, search_box = min((len(values[box]),box) for box in boxes if len(values[box])>1)

    # Use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer
    for digit in values[search_box]:
        temp = values.copy()
        temp = assign_value(temp, search_box, digit)
        attemp = search(temp)
        if attemp:
            return attemp
    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    assignments.append(values.copy())
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
