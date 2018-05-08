import torch
import numpy as np

def no_feedback(pipeline, **kwargs):
	'''
	Returns no action; suitable for dataset wrapper "environments."
	
	Inputs:
	
		| :code:`pipeline` (:code:`bindsnet.pipeline.Pipeline`): Pipeline whose environment accepts no feedback.
	
	Returns:
	
		| :code:`None`.
	'''
	return None

def select_multinomial(pipeline, **kwargs):
	'''
	Selects an action probabilistically based on spiking activity from a network layer.
	
	Inputs:
	
		| :code:`pipeline` (:code:`bindsnet.pipeline.Pipeline`): Pipeline with environment that accepts feedback in the form of actions.
	
	Returns:
	
		| (:code:`int`): Number indicating the desired action from the action space.
	'''
	try:
		output = kwargs['output']
	except KeyError:
		raise KeyError('select_action requires an output layer of size equal to the action space.')
	
	assert pipeline.network.layers[output].n == pipeline.env.action_space.n, 'Output layer size not equal to size of action space.'
	
	spikes = pipeline.network.layers[output].s
	_sum = spikes.sum()
	
	# Choose action based on readout neuron spiking
	if _sum == 0:
		action = np.random.choice(range(pipeline.env.action_space.n))
	else:
		action = torch.multinomial((spikes.float() / _sum.float()).view(-1), 1)[0]
	
	return action

def select_random(pipeline, **kwargs):
	'''
	Selects an action randomly from the action space.
	
	Inputs:
	
		| :code:`pipeline` (:code:`bindsnet.pipeline.Pipeline`): Pipeline with environment that accepts feedback in the form of actions.
	
	Returns:
	
		| (:code:`int`): Number indicating the randomly selected action from the action space.
	'''
	# Choose action randomly from the action space.
	return np.random.choice(range(pipeline.env.action_space.n))