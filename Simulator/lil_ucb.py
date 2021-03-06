import numpy
import random
import sim
import math
import operator

def get_actual_max(arms):
    arms_copy = sorted(arms, key=operator.attrgetter('config_mu'), reverse=True)
    return arms_copy[0]

def calculate_delta(arms, actual_max):
    for arm in arms:
        arm.set_delta(actual_max.get_config_mu() - arm.get_config_mu())

def lil_ucb(students, arms, delta, epsilon, lambda_p, beta, sigma, log_file, max_pulls):
    # delta == confidence
    #
    time = 0
    n = len(arms)
    mu = numpy.zeros(n) # set of rewards
    T = numpy.zeros(n) # T[i] is the number of times arm i has been pulled
    armList = list()
    timestep = 0

    for arm in arms:
        s_arm = sim.LineConfig(arm[0], arm[1], arm[2], arm[3], arm[4])
        s_arm.set_config_mu(students)
        armList.append(s_arm)

    # actual max used for comparison
    actual_max = get_actual_max(armList)
    # set deltas
    calculate_delta(armList, actual_max)

    #sample each of the n arms once, set T_i(t) = 1, for all i and set t=n
    for i in range(n):
        T[i] = 1
        mu[i] = sim.simulate(armList[i], students, log_file) #pull the arm
        log_file.write("ARM: %s\tCONFIGMU %s\tDELTA: %f\n" %(str(armList[i]), armList[i].get_config_mu(), armList[i].get_delta()))
        timestep += 1

    prevIndex = -1;

    while True:
        done = False
        total_pulls = sum(T)
        timestep += 1
        for i in range(n):
            #check if an arm has been pulled more than all others combined
            print("t[i]: %d >= %d\n" %(T[i], (1 + lambda_p*(total_pulls - T[i]))))
            if T[i] >= 1 + lambda_p*(total_pulls - T[i]):
                done = True
                break

        if done:
            break

        index = 0
        upper_bound_value = 0

        for i in range(n):
            #temp is that magic value used to determine the best, next arm to pull
            temp = math.sqrt((2*sigma**2 * (1 + epsilon) * math.log( math.log((1 + epsilon)* T[i])/delta))/T[i])
            temp = mu[i] + (1 + beta)*(1 + math.sqrt(epsilon))*temp

            if(temp > upper_bound_value):
                upper_bound_value = temp
                index = i


        T[index] += 1
        reward = sim.simulate(armList[index], students, log_file)
        mu[index] = ((T[index]-1)*mu[index] + reward) / T[index] #average the rewards

        if(timestep % 100 == 0):
            #log_file.write("ITERATION: %6d ARM: %s\tCONFIGMU: %f\tDELTA: %f\n" %(timestep, str(armList[index]), armList[index].get_config_mu(), armList[index].get_delta()))
            empercial_best = max(mu)
            best_arm_index = [i for i,j in enumerate(mu) if j == empercial_best]
            best_arm = armList[best_arm_index[0]]
            log_file.write("ITERATION: %6d\tBEST_ARM: %s\tCONFIG_MU: %f\tDELTA: %f\n" %(timestep, str(best_arm), best_arm.get_config_mu(), best_arm.get_delta()))


        #prevIndex = index
        if(timestep == max_pulls):
            break

    arm = armList[T.argmax()]
    log_file.write("\nBEST ARM: %s\tCONFIG_MU: %f\tDELTA: %f\n"
            %(str(arm), arm.get_config_mu(), arm.get_delta()))

    for count,arm in enumerate(armList):
        log_file.write("ARMPULLCOUNT: %s\t%d\n" %(str(arm), T[count]))

    return armList[T.argmax()]
