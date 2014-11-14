import numpy
import random
import sample_arm
import sim
import operator

def pick_arm(arms, epsilon):
	# 1 - epsilon percent of the time choose greedily
	# otherwise randomly choose an arm
	if (random.random() >= epsilon):
		# choose greedily
		return 0
	else:
		# choose randomly
		return random.randint(0, len(arms) - 1)

def epsilon_greedy(arms, bound, epsilon):
	"""
	arms is a list of configurations, each config can be passed as a
	numpy array.
	bound is the number of arm pulls we will limit ourselves to
	"""
	# build list of sampleArm objects to track rewards and averages
	s = list()
	for arm in arms:
		s_arm = sample_arm.sampleArm(arm)
		s.append(s_arm)

	for i in range(bound):
		# because we are not using a simple numpy.array we will sort
		# the list in place on each interval (ineffeciennnncy)
		# to get the greedy arm
		j = pick_arm(s, epsilon)
		s[j].set_num_pulls(s[j].get_num_pulls() + 1)

		# pull the arm
		reward = sim.simulate(s[j].get_arm())
		s[j].set_total_reward(
				s[j].get_total_reward() + reward)
		s[j].set_average(
				s[j].get_total_reward() / s[j].get_num_pulls())

		# sort the arms
		s.sort(key=operator.attrgetter('average'), reverse=True)

	# return the best arm
	for arm in s:
		print(arm.get_average())
	return s[0].get_arm()