import pandas as pd
from simulation import SimAccount, AverageCrossover

"""
For each function, input units must be scaled with respect to one another; any
discrete units must be specified, the solution to this may just be to round it
to an integer (or whatever discrete value it needs to be)
"""

def optimize_avg_cross(data):

    # design variable 1 step size tolerance
    var1_tol = 2

    # to store results from simulations, prevents same simulation from being run twice (very important for expensive simulations)
    repeats = pd.DataFrame(columns=['lavg', 'savg', 'fval'])

    # set min and max values for design variables if needed
    min_lavg = 1
    max_lavg = 90
    min_savg = 1
    max_savg = 20

    # initial design variable values;
    # these variables hold values of design variables at the center of pattern search iterations
    center_lavg = 15
    center_savg = 5
    # run simulation for initial center values and store values
    avgco = AverageCrossover(data, center_lavg, center_savg)
    account = avgco.run_sim()
    length = len(account.avg_total_val)
    center_fval = account.avg_total_val[length-1]
    repeats = repeats.append({'lavg':center_lavg, 'savg':center_savg, 'fval':center_fval}, ignore_index=True)

    # ratio used to normalize the step sizes of design variables wrt design variable 1;
    # bti step to gratio step
    v1_to_v2 = 1
    # initialize step sizes
    lavg_step = 5
    savg_step = lavg_step * v1_to_v2

    # this loop runs until pattern search optimization termination conditions are met
    while True:
        # initialize *empty* samples dataframe;
        # to store test samples during pattern search iterations
        samples = pd.DataFrame(columns=['lavg', 'savg', 'fval'])
        # take sample steps in every direction
        for dir1 in [-1, 0, 1]:
            lavg = int(center_lavg + dir1 * lavg_step)
            # conditions for lavg to be valid
            if lavg < max_lavg and lavg > min_lavg:
                for dir2 in [-1, 0, 1]:
                    savg = int(center_savg + dir2 * savg_step)
                    # conditions for savg to be valid
                    if savg < max_savg and savg > min_savg and lavg > savg:
                        # all design variables are valid;
                        # append design variable sample to samples dataframe for testing
                        samples = samples.append({'lavg':lavg, 'savg':savg}, ignore_index=True)
        # performance metric for the best sample
        best_fval = center_fval
        # long average value corresponding to the best sample
        best_lavg = center_lavg
        # short average value corresponding to the best sample
        best_savg = center_savg
        # test samples
        for i in range(len(samples)):
            lavg = int(samples['lavg'][i])
            savg = int(samples['savg'][i])
            # test if sample has already been tested;
            # attempts to extract this information from the repeats dataframe;
            # if successful, it will contain the sample that has already been tested
            test_rep = repeats.loc[(repeats['lavg'] == lavg) & (repeats['savg'] == savg)]
            # if there was no prior simulation of the sample
            if test_rep.empty:
                # initialize simulation
                avgco = AverageCrossover(data, lavg, savg)
                # run simulation
                account = avgco.run_sim()
                # calculate length of total value array
                length = len(account.avg_total_val)
                # set most recent average total value, this is our performance metric
                fval = account.avg_total_val[length-1]
                # add fval to 'samples' dataframe
                samples['fval'][i] = fval
                # add simulation results to 'repeats' dataframe
                repeats = repeats.append({'lavg':lavg, 'savg':savg, 'fval':fval}, ignore_index=True)
            # else this sample has already been simulated and the result was stored
            else:
                # set average total value from prior simulation
                samples['fval'][i] = test_rep['fval'].iloc[0]

            fval = samples['fval'][i]
            # if better performing sample is found, track results
            if fval > best_fval:
                best_fval = fval
                best_lavg = lavg
                best_savg = savg
        # if a better performing sample was found, it becomes the new center
        if best_fval > center_fval:
            # step size increased by a factor of 2
            lavg_step = lavg_step * 2
            savg_step = savg_step * 2
            # best sample becomes the center for the next pattern search iteration
            center_fval = best_fval
            center_lavg = best_lavg
            center_savg = best_savg
        # better performing sample not found, same center for next pattern search iteration
        else:
            # step size decreased by a factor of 2
            # step size increased by a factor of 2
            lavg_step = lavg_step / 2
            savg_step = savg_step / 2
        # TERMINATION CONDITIONS
        # if design variable 1 step size is less than the tolerance
        if lavg_step < var1_tol:
            # return optimum design variables
            return center_lavg, center_savg
