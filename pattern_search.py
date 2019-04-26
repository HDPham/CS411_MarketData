from simulation import SimAccount, DUMM
"""
For each function, input units must be scaled with respect to one another; any
discrete units must be specified (e.g.: bti in DUMM), the solution to this may
just be to round it to an integer (or whatever discrete value it needs to be)
"""

# maximum number of iterations
max_iter = 10000
# step size tolerance
x_tol = 0.001

max_bti = 90
min_bti = 1
bti0 = 5

gratio0 = 2
min_gratio = 1

bti_init = 5
gratio_init = 3

# ratio used to normalize the step sizes of design variables
# bti step to gratio step
v1_to_v2 = 1
# initialize step sizes
gratio_step = 1
bti_step = gratio_step * v1_to_v2
