# =============================================================================
# Corrplot.py
#
#
# displays a correlation plot for genome data that has been saved
# using numpy, for instance
# np.savez(sys.argv[1], genome=alg.genome, ospace=alg.ospace, fitnesses=alg.fitnesses)
# -----------------------------------------------------------------------------


import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import scipy.stats as st


class Corrplot: 
	def __init__(self, genome_info): 
		genome = genome_info["genome"]
		ospace = genome_info["ospace"]			
		self._variables  = genome.shape[1]
		self._objectives = ospace.shape[1]
		self._data = np.append(genome, ospace, axis=1)
		
		self._fig = plt.figure(1)
		rect = self._fig.patch
		rect.set_facecolor("white")
		self._ax = self._fig.add_subplot(1,1,1)
		self._ax.set_title("Correlations (Pearson's r)")

		self.find_correlations()
		
	def show(self):
		labels = ["Variable " + str(i) for i in range(self._variables)]
		labels.extend(["Objective " + str(i) for i in range(self._objectives)])
		plt.xticks(range(self._data.shape[1]), labels, rotation="vertical")
		plt.yticks(range(self._data.shape[1]), labels)
		img = plt.imshow(self.correlations, cmap=plt.get_cmap("RdGy"), interpolation="nearest")		
		plt.colorbar(img)
		plt.grid(True)
		plt.show()
		
	def find_correlations(self): 
		n = self._data.shape[1]
		self.correlations = np.zeros((n,n))
		self.pval = np.zeros((n,n))
		for i in range(n): 
			self.pval[i,i] = 1
			for j in range(i): 
				pr = st.pearsonr(self._data[:,i], self._data[:,j])
				self.correlations[i,j] = self.correlations[j,i] = np.round(pr[0], 2)
				self.pval[i,j] = self.pval[j,i] = np.round(1-pr[1],2)
					
	
		
if __name__ == "__main__":
	if not len(sys.argv) == 2: 
		print "usage: corrplot.py <npz file>"
	else:
		plot = Corrplot(np.load(sys.argv[1]))
		print("\nCorrelations")
		print(plot.correlations)
		print("\np-value of estimated correlations")
		print(plot.pval)
		print("")
		plot.show()
