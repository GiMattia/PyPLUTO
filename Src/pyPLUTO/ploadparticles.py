#!/usr/bin/python3
from __future__ import division
import os
import sys
import numpy as np

class ploadparticles(object):
	def __init__(self, ns, w_dir=None, datatype=None, ptype=None, chnum=None):
		"""
		Loads the Particle datafile.

		**Inputs**:
		ns 	-- Step Number of the data file\n
		w_dir 	 -- path to the directory which has the data files\n
		datatype -- Datatype (default is set to read .dbl data files)
		ptype 	 -- A string denoting the type of particles ('LP', 'CR', 'DUST' etc. Default is 'CR')
		chnum    -- 2 digit integer denoting chunk number
		(Only used if ptype = 'LP' to read particles.nnnn_chxx.dbl file, where nnnn is 4 digit integer denotong ns and xx is a 2 digit integer for chunk number : Default value is 0)
		
		**Outputs**:
		pyPLUTO pload object whose keys are arrays of data values.
		"""
		self.Nstep = ns
		if w_dir is None:
			w_dir = os.getcwd() + '/'
		self.wdir = w_dir
		if datatype is None:
			datatype = "dbl"
		self.datatype = datatype
		if ptype == 'LP' and self.datatype in ['dbl', 'flt']:
			if chnum is None: chnum = 0 #by default it reads first file. 
			self.fname = self.wdir+"particles.%04d_ch%02d.%s"%(ns, chnum, self.datatype)
		else:
			self.fname = self.wdir+"particles.%04d.%s"%(ns, self.datatype)
		if self.datatype == 'vtk':
			Part_dictionary = self.ReadVTKParticleFile()
		else:
			Part_dictionary = self.ReadBinParticleFile()
		for keys in Part_dictionary:
			object.__setattr__(self, keys, Part_dictionary.get(keys))

	def ReadVTKParticleFile(self):
		print("Reading particle file : %s"%self.fname)
		fp = open(self.fname,'rb')
		nfields = 0
	
		while True:
			line = fp.readline()
			try:
				line.split()[0]
			except IndexError as error:
				pass
			else:
				if line.split()[0] == b'POINTS':
					nparts = int(line.decode().split()[1])
					dtype_tup = str(nparts*3)+'>f4'
					nb = np.dtype(dtype_tup).itemsize
					vtkvar_buf = np.frombuffer(fp.read(nb), dtype=np.dtype(dtype_tup))
					coords = vtkvar_buf.reshape(nparts,3)
					val_dict = {'Totparticles':nparts, 'x1':coords[:,0],'x2':coords[:,1],'x3':coords[:,2]}
					nfields += 3
				
				if line.split()[0] == b'SCALARS':
					vars = line.decode().split()[1]
				if line.split()[0] == b'LOOKUP_TABLE':
					if vars == 'Identity': 
						dtype_tup = str(nparts)+'>i4'
						field_name = 'id'
					elif vars == 'tinj': 
						dtype_tup = str(nparts)+'>f4'
						field_name = 'tinj'
					elif vars == 'Color': 
						dtype_tup == str(nparts)+'>f4'
						field_name = 'color'
					nb = np.dtype(dtype_tup).itemsize
					vtkvar_buf = np.frombuffer(fp.read(nb), dtype=np.dtype(dtype_tup))
					val_dict.update({field_name:vtkvar_buf})
					nfields += 1
				if line.split()[0] == b'VECTORS':
					vars = line.decode().split()[1]
					dtype_tup = str(nparts*3)+'>f4'
					nb = np.dtype(dtype_tup).itemsize
					vtkvar_buf = np.frombuffer(fp.read(nb), dtype=np.dtype(dtype_tup))
					vels = vtkvar_buf.reshape(nparts,3)
					val_dict.update({'vx1':vels[:,0], 'vx2':vels[:,1], 'vx3':vels[:,2]})
					nfields += 3
				else:
					pass
			if line == b'':
				break
		val_dict.update({'nfields':nfields})
		return val_dict

	def ReadBinParticleFile(self):
		print("Reading particle file : %s"%self.fname)
		fp = open(self.fname, "rb")
		val_dict = {}
		h_lines = 0

		#READ HEADER. 
		with open(self.fname,"rb") as f:
			for line in f:
				if line.startswith(b'#'):
					if line.split()[1] != b'PLUTO': 
						val_dict.update({line.split()[1].decode('utf8'):[i.decode('utf8') for i in line.split()[2:]]})
					h_lines += 1
		
		#SKIP HEADER LINES	
		cnt = 0
		while (cnt < h_lines):
			fp.readline()
			cnt += 1
        
		#READ DATA
		data_ = fp.read()
		fp.close()

		#SORT DATA INTO DICTIONARY BASED ON DATATYPE.
		if self.datatype == 'flt':
			dt = np.dtype({'names':val_dict['field_names'], 'formats':['('+i+',)<f' for i in val_dict['field_dim']]})
		else:
			dt = np.dtype({'names':val_dict['field_names'], 'formats':['('+i+',)<d' for i in val_dict['field_dim']]})

		val_ = np.frombuffer(data_,dtype=dt)

		for i in range(len(val_dict['field_names'])):
			name = val_dict['field_names'][i]
			if int(val_dict['field_dim'][i]) == 1:
				val_dict.update({name:val_[name].flatten()})
			else:
				val_dict.update({name:val_[name]})

		#OUTPUT IS A DICTIONARY. 
		return val_dict



		

