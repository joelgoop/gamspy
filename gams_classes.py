import os
import subprocess as sp
from PySide import QtCore

class GamsModel(object):
	"""Class that contains necessary data to run a GAMS model"""
	def __init__(self, gams_dir, model_file, res_file):
		super(GamsModel, self).__init__()
		self.gams_dir = os.path.abspath(gams_dir)
		os.chdir(self.gams_dir)
		self.model_file = model_file
		self.res_file = res_file

	# Property containing the model file name
	def model_file():
		doc = "The model_file property."
		def fget(self):
			return self._model_file
		def fset(self, value):
			if os.path.isfile(self.gams_dir+'/'+value):
				if 'gms'==os.path.splitext(value)[1][1:]:
					self._model_file = value
				else:
					raise Exception('Model file type is not .gms.\n'+value)
			else:
				raise Exception('Model file does not exist.\n'+value)
		def fdel(self):
			del self._model_file
		return locals()
	model_file = property(**model_file())

	# Property containing the result file name
	def res_file():
	    doc = "The res_file property."
	    def fget(self):
	        return self._res_file
	    def fset(self, value):
	        self._res_file = value
	    def fdel(self):
	        del self._res_file
	    return locals()
	res_file = property(**res_file())



class GamsThread(QtCore.QThread):
	"""Class to run GAMS in a separate QThread"""

	#gams_finished = QtCore.Signal()

	# Constructor
	def __init__(self,model):
		super(GamsThread, self).__init__()
		self.model = model

	# Run thread
	def run(self):
		os.chdir(self.model.gams_dir)
		sp.call(["gams", self.model.model_file])
		self.read_results()
	#	self.gams_finished.emit()

	# Returns results dictionary
	def get_results(self):
		return self._results

	# Read results from the put file generated from GAMS
	def read_results(self):
		f = open(self.model.res_file,'r')
		self._results = dict()
		for line in f:
			parts = line.split()
			self._results = self.make_dict(parts,self._results)
		f.close()

	def make_dict(self,current_list,level_above):
		if len(current_list)==2:
			level_above[current_list[0]] = float(current_list[1])
			return level_above
		else:
			if not level_above.has_key(current_list[0]):
				level_above[current_list[0]]=dict()
			level_above[current_list[0]] = self.make_dict(current_list[1:],level_above[current_list[0]])
			return level_above
