from random import random

def make_grid(L):
    """TESTED: generate a grid of size LxL
    input:
            L = size of grid
    output:
            stab = LxL grid of stabilizers with 0(no error)
                qubits are between stabilizers
            qubits = 2LxL grid of qubits
            """

    stab = [[0 for col in range(L)] for row in range(L)]
    qubits = [[0 for col in range(L)] for row in range(2*L)]

    return stab, qubits 


def print_grid_stab(grid):
    """TESTED: print the stabilizer grid"""
    print ('-' * len (grid[0]))
    for row in grid:
        st = ' '.join([str(elem) for elem in row])
        print(st)
    print('-' * len(grid[0]))

    
def print_grid_qubits(grid):
    """TESTED: print the qubit grid"""
    print ('-' * len(grid[0])*3)

    for i in range(len(grid)//2):

        if i % 2 == 0:
            print(' ' + ' '.join([str(x) for x in grid[i]]))

        else:
            print(' '.join([str(x) for x in grid[i]]) + ' ')

        # Alternate way to print qubits in two rows
        # print(' '.join([str(elem) for elem in grid[2*i]]))
        # print(' '.join([str(elem) for elem in grid[2*i + 1]]))
        # print('-' * len(grid[0])*3)
    print ('-' * len(grid[0])*3)

def generate_random_errors(grid_s,grid_q, px, pz):
    """TESTED: Generate random errors on qubits, and adds 1 to the stabilizers
    if an error on neighbouring qubit occured
    Input:
            grid: LxL grid of stabilizers
            px: probability to have an error on a qubits
    Output:
            grid_s: LxL grid of stabilizers, with values 0-4 for 0-4 errors
                on neighbouring qubits
            grid_q: 2LxL grid of qubits, with values 0-1 for 0 or 1 error on the qubits
            """

    # Loop trough all qubits:
    for row_idx in range(len(grid_q)):
        for col_idx in range(len(grid_q[0])):
            error = random() <= px

            if not error:
                # Nothing has to be changed 
                continue
            if row_idx % 2 == 0:
                # above/under stabilizers -> same column 
                stab_row = int(row_idx/2)
                grid_s[stab_row][col_idx] += 1 # Stabilizer under qubit 
                grid_s[stab_row - 1][col_idx] += 1 # Stabilizer above qubit
            else:
                # left/right stabilizers -> same row
                stab_row = int((row_idx - 1)/2)
                grid_s[stab_row][col_idx] += 1 # Stabilizer right of qubit
                grid_s[stab_row][col_idx - 1] += 1 # Stabilizer left of qubit
            grid_q[row_idx][col_idx] += 1 # Mark error on qubit
    return grid_s, grid_q

def check_correction(grid_q):
    """(tested for random ones):Check if the correction is correct(no logical X gates)
    input:
        grid_q: grid of qubit with errors and corrections
    output:
        corrected: boolean whether correction is correct.
    """
    # correct if even times logical X1,X2=> even number of times through certain edges
    # upper row = X1
    if sum(grid_q[0]) % 2 != 0:
        return (False,'X1 error')
    # odd rows = X2
    if sum([grid_q[x][0] for x in range(1,len(grid_q),2)]) == 1:
        return (False,'X2 error')
    
    # and if all stabilizers give outcome +1 => even number of qubits filps for each sabilizer 
    # is this needed really? or assume given stabilizer outcome is corrected for sure?
    for row_idx in range(len(grid_q)//2):
        for col_idx in range(len(grid_q[0])):
            all_errors = 0 
            all_errors += grid_q[2*row_idx][col_idx] # above stabilizer 
            all_errors += grid_q[2*row_idx + 1][col_idx] # left of stabilizer
            if row_idx < int(len(grid_q)/2) - 1: # not the last row
                all_errors += grid_q[2*(row_idx + 1)][col_idx] # below stabilizer
            else: # last row
                all_errors += grid_q[0][col_idx] # below stabilizer (wrap around)
            if col_idx < len(grid_q[2*row_idx +1 ]) - 1: # not the last column
                all_errors += grid_q[2*row_idx + 1][col_idx + 1] # right of stabilizer
            else: # last column
                all_errors += grid_q[2*row_idx + 1][0] # right of stabilizer (wrap around)
            if all_errors % 2 == 1:
                return (False,'Stabilizer error at ({},{})'.format(row_idx,col_idx)) # stabilizer not +1
    return (True,'No logical error detected')

# ==========================================
# TEST SCRIPT
# ==========================================
if __name__ == "__main__":
    print("\n=== TEST 1: Single Qubit Error (Geometry Check) ===")
    L = 5
    s_grid, q_grid = make_grid(L)
    
    # Let's manually inject ONE error in the middle of the grid
    # Row 4, Col 2 (This is roughly the center for L=5)
    q_grid[4][2] = 1 
    
    # We use your function to update the stabilizers based on this error
    # We pass p=0 so no NEW random errors are added, we just want to update the stabilizers
    s_grid, q_grid = generate_random_errors(s_grid, q_grid, px=0, pz=0)

    print("Qubit Grid (Notice the '1' in the middle):")
    print_grid_qubits(q_grid)
    
    print("\nStabilizer Grid (Should see two '1's outlining the error):")
    print_grid_stab(s_grid)
    
    # Check what the verification function thinks
    valid, message = check_correction(q_grid)
    print(f"\nResult: {valid} -> {message}") 
    # EXPECTED: False (Stabilizer error), because we have 2 unhappy stabilizers.


    print("\n" + "="*40)
    print("=== TEST 2: Logical Error (Detection Check) ===")
    # Reset grids
    s_grid, q_grid = make_grid(L)

    # Manually create a LOGICAL X1 Error (Horizontal chain)
    # We fill the entire first row with errors. 
    # This loops around the torus.
    for i in range(L):
        q_grid[0][i] = 1
    
    print("Qubit Grid (Top row full of errors):")
    print_grid_qubits(q_grid)

    # Verify logic
    valid, message = check_correction(q_grid)
    print(f"\nResult: {valid} -> {message}")
    # EXPECTED: False (X1 error). 
    # Even though stabilizers are happy (syndrome is 0), the logic failed.


    print("\n" + "="*40)
    print("=== TEST 3: Stabilizer Loop (Trivial Error) ===")
    # Reset grids
    s_grid, q_grid = make_grid(L)

    # Manually create a small loop (a stabilizer operation).
    # This acts like "Nothing happened" logically.
    # A loop is formed by 4 qubits around a plaquette.
    # Coordinates depend on your specific layout, but let's try a small square:
    q_grid[0][0] = 1
    q_grid[1][0] = 1 # vertical edge
    q_grid[1][1] = 1 # vertical edge next to it
    q_grid[2][0] = 1 # bottom edge
    # Note: Precise coordinates for a loop depend on your 2L x L mapping
    
    valid, message = check_correction(q_grid)
    # If the loop is perfect, this should be True. 
    # If I missed an edge in manual mapping, it will be False.
    print(f"Result for manual loop: {valid} -> {message}")
    