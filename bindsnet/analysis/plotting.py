import sys
import torch
import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable


plt.ion()

def plot_input(image, inpt, ims=None, figsize=(8, 4)):
	'''
	Plots a two-dimensional image and its corresponding spike-train representation.
	
	Inputs:
		image (torch.Tensor or torch.cuda.Tensor): A two-dimensional
			array of floating point values depicting an input image.
		inpt (torch.Tensor or torch.cuda.Tensor): A two-dimensional array of
			floating point values depicting an image's spike-train encoding.
		ims (list(matplotlib.image.AxesImage)): Used for re-drawing the input plots.
		figsize (tuple(int)): Horizontal, vertical figure size in inches.
	
	Returns:
		(list(matplotlib.image.AxesImage)): Used for re-drawing the input plots.
	'''
	if not ims:
		fig, axes = plt.subplots(1, 2, figsize=figsize)
		ims = axes[0].imshow(image, cmap='binary'), axes[1].imshow(inpt, cmap='binary')
		
		axes[0].set_title('Current image')
		axes[1].set_title('Poisson spiking representation')
		axes[1].set_xlabel('Simulation time'); axes[1].set_ylabel('Neuron index')
		axes[1].set_aspect('auto')
		
		for ax in axes:
			ax.set_xticks(()); ax.set_yticks(())
		
		fig.tight_layout()
	else:
		ims[0].set_data(image)
		ims[1].set_data(inpt)

	return ims


def plot_spikes(spikes, ims=None, axes=None, time=None, n_neurons={}, figsize=(8, 4.5)):
	'''
	Plot spikes for any group(s) of neurons.

	Inputs:
		spikes (dict(torch.Tensor or torch.cuda.Tensor)): Contains
			spiking data for groups of neurons of interest.
		ims (list(matplotlib.image.AxesImage)): Used for re-drawing the spike plots.
		axes (list(matplotlib.axes.Axes)): Used for re-drawing the spike plots.
		time (tuple(int)): Plot spiking activity of neurons between the given range
			of time. Default is the entire simulation time. For example, time = 
			(40, 80) will plot spiking activity of neurons from 40 ms to 80 ms.
		figsize (tuple(int)): Horizontal, vertical figure size in inches.
		n_neurons (dict(tuple(int))): CPlot spiking activity of neurons between the
		   given range of neurons. Default is all neurons of the layer. For example,
		   (10, 25) will plot spiking activity of neurons between those range of
		   indices. Don't need to provide number of neurons for all layers. Default
			will be chosen if not provided.
	
	Returns:
		(list(matplotlib.image.AxesImage)): Used for re-drawing the spike plots.
		(list(matplotlib.axes.Axes)): Used for re-drawing the spike plots.
	'''
	n_subplots = len(spikes.keys())
   
   # Time setup
	if time is not None: 
       # Confirm only 2 values for time were given
		assert(len(time) == 2)
       # First value must be less than the second 
		assert(time[0] < time[1])
	
	else: # Set it for entire duration
		for key in spikes.keys():
			time = (0, spikes[key].shape[1])
			break

	# Number of neurons setup
	if n_neurons is not None:
		# Don't have to give numbers for all keys
		assert(len(n_neurons.keys()) <= n_subplots)
		# Keys given must be same as the ones used in spikes dict
		assert(all(key in spikes.keys() for key in n_neurons.keys())==True)
		# Checking to that given n_neurons per neuron layer is valid
		assert(all(n_neurons[key][0] >= 0 and n_neurons[key][1] <= val.shape[0] for key, val in spikes.items() if key in n_neurons.keys()) == True)
	
	#else: # Uses default values using spikes dict
	for key, val in spikes.items():
		if key not in n_neurons.keys():
			n_neurons[key] = (0, val.shape[0])
    
	if not ims:
		fig, axes = plt.subplots(n_subplots, 1, figsize=figsize)
		ims = []
		
		if n_subplots == 1: # Plotting only one image
			for datum in spikes.items():
				ims.append(axes.imshow(spikes[datum[0]][n_neurons[datum[0]][0]:n_neurons[datum[0]][1], time[0]:time[1]], cmap='binary'))
				plt.title('%s spikes for neurons (%d - %d) from t = %1.2f ms to %1.2f ms '% (datum[0], n_neurons[datum[0]][0], n_neurons[datum[0]][1], time[0], time[1]))
				plt.xlabel('Time (ms)'); plt.ylabel('Neuron index')
				axes.set_aspect('auto')
		else: # Plot each layer at a time
			for i, datum in enumerate(spikes.items()):
				ims.append(axes[i].imshow(datum[1][n_neurons[datum[0]][0]:n_neurons[datum[0]][1], time[0]:time[1]], cmap='binary'))
				axes[i].set_title('%s spikes for neurons (%d - %d) from t = %1.2f ms to %1.2f ms '% (datum[0], n_neurons[datum[0]][0], n_neurons[datum[0]][1], time[0], time[1]))
			
			for ax in axes:
				ax.set_aspect('auto')
			
		plt.setp(axes, xticks=[], yticks=[], xlabel='Simulation time', ylabel='Neuron index')
		
		plt.tight_layout()
           
	else: # Plotting figure given
		assert(len(ims) == n_subplots)
		for i, datum in enumerate(spikes.items()):
				ims[i].set_data(datum[1][n_neurons[datum[0]][0]:n_neurons[datum[0]][1], time[0]:time[1]])
				axes[i].set_title('%s spikes for neurons (%d - %d) from t = %1.2f to %1.2f '% (datum[0], n_neurons[datum[0]][0], n_neurons[datum[0]][1], time[0], time[1]))
	
	return ims, axes
        

def plot_weights(weights, wmin=0.0, wmax=1.0, im=None, figsize=(5, 5)):
	'''
	Plot a (possibly reshaped) connection weight matrix.
	
	Inputs:
		weights (torch.Tensor or torch.cuda.Tensor): Weight matrix of Connection object.
		wmin (float): Minimum allowed weight value.
		wmax (float): Maximum allowed weight value.
		im (matplotlib.image.AxesImage): Used for re-drawing the weights plot.
		figsize (tuple(int)): Horizontal, vertical figure size in inches.
	
	Returns:
		(matplotlib.image.AxesImage): Used for re-drawing the weights plot.
	'''
	if not im:
		fig, ax = plt.subplots(figsize=figsize)
		
		im = ax.imshow(weights, cmap='hot_r', vmin=wmin, vmax=wmax)
		div = make_axes_locatable(ax)
		cax = div.append_axes("right", size="5%", pad=0.05)
		
		ax.set_xticks(()); ax.set_yticks(())
		
		plt.colorbar(im, cax=cax)
		fig.tight_layout()
	else:
		im.set_data(weights)

	return im


def plot_assignments(assignments, im=None, figsize=(5, 5)):
	'''
	Plot the two-dimensional neuron assignments.
	
	Inputs:
		assignments (torch.Tensor or torch.cuda.Tensor): Vector of neuron label assignments.
		im (matplotlib.image.AxesImage): Used for re-drawing the assignments plot.
		figsize (tuple(int)): Horizontal, vertical figure size in inches.
	
	Returns:
		(matplotlib.image.AxesImage): Used for re-drawing the assigments plot.
	'''
	sqrt = int(np.sqrt(assignments.size(0)))
	assignments = assignments.view(sqrt, sqrt).t()
	
	if not im:
		fig, ax = plt.subplots(figsize=figsize)

		color = plt.get_cmap('RdBu', 11)
		im = ax.matshow(assignments, cmap=color, vmin=-1.5, vmax=9.5)
		div = make_axes_locatable(ax); cax = div.append_axes("right", size="5%", pad=0.05)
		plt.colorbar(im, cax=cax, ticks=np.arange(-1, 10))
		
		ax.set_xticks(()); ax.set_yticks(())
		
		fig.tight_layout()
	else:
		im.set_data(assignments)

	return im


def plot_performance(performances, ax=None, figsize=(7, 4)):
	'''
	Plot training accuracy curves.
	
	Inputs:
		performances (dict(list(float))): Lists of training accuracy estimates per voting scheme.
		ax (matplotlib.axes.Axes): Used for re-drawing the performance plot.
		figsize (tuple(int)): Horizontal, vertical figure size in inches.
	
	Returns:
		(matplotlib.axes.Axes): Used for re-drawing the performance plot.
	'''
	if not ax:
		_, ax = plt.subplots(figsize=figsize)
	else:
		ax.clear()

	for scheme in performances:
		ax.plot(range(len(performances[scheme])), [p for p in performances[scheme]], label=scheme)

	ax.set_ylim([0, 100])
	ax.set_title('Estimated classification accuracy')
	ax.set_xlabel('No. of examples'); ax.set_ylabel('Accuracy')
	ax.set_xticks(()); ax.set_yticks(range(0, 110, 10))
	ax.legend()

	return ax

def plot_general(monitors=None):
	if monitors is None:
		print ("Did you forget to provide monitors?")
		
def plot_voltages(voltages, ims=None, axes=None, time=None, figsize=(8, 4.5)):
	'''
	Plot voltages for any group(s) of neurons.

	Inputs:
		voltages (dict(torch.Tensor or torch.cuda.Tensor)): Contains
			voltage data for layers of neurons of interest.
		ims (list(matplotlib.image.AxesImage)): Used for re-drawing the spike plots.
		axes (list(matplotlib.axes.Axes)): Used for re-drawing the spike plots.
		time (tuple(int)): Plot spiking activity of neurons between the given range
			of time. Default is the entire simulation time. For example, time = 
			(40, 80) will plot spiking activity of neurons from 40 ms to 80 ms.
		figsize (tuple(int)): Horizontal, vertical figure size in inches.
	
	Returns:
		(list(matplotlib.image.AxesImage)): Used for re-drawing the voltage plots.
		(list(matplotlib.axes.Axes)): Used for re-drawing the voltage plots.
	'''
	n_subplots = len(voltages.keys())
    
	# Confirm only 2 values for time were given
	if time is not None: 
		assert(len(time) == 2)
		assert(time[0] < time[1])

	else: # Set it for entire duration
		for key in voltages.keys():
			time = (0, voltages[key].shape[0])
			break
	
	if not ims:
		fig, axes = plt.subplots(n_subplots, 1, figsize=figsize)
		ims = []
		
		if n_subplots == 1: # Plotting only one image
			for key in voltages.keys():
				ims.append(axes.plot(voltages[key][:, time[0]:time[1]]))
				plt.title('%s voltages from t = %d to %d' % (key, time[0], time[1]))
				plt.xlabel('Time (ms)'); plt.ylabel('Neuron index')

		else: # Plot each layer at a time
			for i, datum in enumerate(voltages.items()):
				ims.append(axes[i].plot(datum[1][:, time[0]:time[1]]))
				axes[i].set_title('%s voltages from t = %d to %d' % (datum[0], time[0], time[1]))

		plt.setp(axes, xticks=[], yticks=[], xlabel='Simulation time', ylabel='Neuron index')
		
		for ax in axes:
			ax.set_aspect('auto')
		
		plt.tight_layout()
           
	else: # Plotting figure given
		assert(len(ims) == n_subplots)
		for i, datum in enumerate(voltages.items()):
			axes[i].clear()
			
			if time is None:
				axes[i].plot(datum[1])
				axes[i].set_title('%s voltages from t = %d to %d' % (datum[0], time[0], time[1]))
			else: # Plot for given time
				axes[i].plot(datum[1][time[0]:time[1]])
				axes[i].set_title('%s voltages from t = %d to %d' % (datum[0], time[0], time[1]))
	
	return ims, axes