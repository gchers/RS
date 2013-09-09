###############
#             #
#############################
# File:   images_util.py	#
# Author: Giovanni Cherubin	#
import Tkinter
import spectral
import Image
import numpy

def overlay_images_alpha(img1, img2):
	img1 = photoimage2image(img1)
	img2 = photoimage2image(img2)
	img1.convert('RGBA')
	img2.convert('RGBA')
	new = Image.blend(img1,img2,0.5)
	return image2photoimage(new)

def overlay_images(img1, img2):
	img = Tkinter.PhotoImage(width=img1.width(),height=img1.height())
	for j in xrange(img1.height()):
		for i in xrange(img2.width()):
			if img2.get(i,j) != u'0 0 0':
				color = [int(c) for c in img2.get(i,j).split()]
				put_pixel(img,color,(i,j))
			else:
				color = [int(c) for c in img1.get(i,j).split()]
				put_pixel(img,color,(i,j))
	return img

def photoimage2image(photo):	
	data = [tuple(int(p) for p in photo.get(col,row).split()) for row in xrange(photo.height())
								for col in xrange(photo.width())]
	img = Image.new('RGB',(photo.width(),photo.height()))
	img.putdata(data)
	return img

def image2photoimage(img):
	width, height = img.size
	photo = Tkinter.PhotoImage(width=width, height=height)
	for j in xrange(height):
		for i in xrange(width):
			put_pixel(photo,img.getpixel((i,j)),(i,j))
	return photo	


def normalize_matrix(m,to=255):
	'''Normalizes a matrix (numpy.ndarray)
	between 0 and 255.'''
	m = m + abs(numpy.amin(m))
	m = m*to/numpy.amax(m)
	return m


def put_pixel(photo, color, pos):
		if isinstance(color, (tuple,list)):
			r,g,b 	= color
		else:
			r = g = b = color
		row,col = pos
		hexcode = "#%02x%02x%02x" % (r,g,b)
		photo.put(hexcode, (row,col))


class RemoteSensingImage():

	def __init__(self, fn, maxsize):
		self.maxsize = maxsize # this is the max size (X,Y) one image can be given
		self.img 	= self._open_image(fn)
		self.meta	= self.img.metadata
		self.truecolImage = None
		self.size = (self.img.nrows, self.img.ncols)
		self.nbands =  self.img.nbands
		self.band 	= {}
		#self.bandn  = [b.upper() for b in self.img.metadata['band names']]
		
		for i in xrange(self.nbands):
			self.band[i] = abs(numpy.float32(self.img.read_band(i)))
	
	def _open_image(self,fn):
		return spectral.envi.open(fn)
	
	def resize_image(self, photo):
		'''If photo image is too big, according
		to self.maxsize, it is resized.'''
		# For this version we're not resizing in this
		# way. The crop is done from gui
		return photo
		#w,h = self.maxsize
		#print photo.width(),photo.height()
		#p = photo
		#if (p.width() > w) and (p.height() > h):
			#i = photoimage2image(p).resize((w,h))
			#p = image2photoimage(i)
			#p = p.subsample(0.5,0.5)#float(w)/p.width(),float(h)/p.height())
			#print p.width(),p.height()
		#return p
		
	def get_true_colors(self):
		'''Returns a PhotoImage using RGB
		bands. If a band is missing an
		exception is raised by
		self.require_bands().'''
		checkbands = ['R','G','B']
		missing = []
		for i in checkbands:
			if self.get_band_index(i) == -1:
				missing.append(i)
		if len(missing) > 0:
			raise Exception('Missing band',missing) 
			
		if self.truecolImage == None:
			#self.require_bands(['R','G','B'])
			R = self.get_band_index('R')
			G = self.get_band_index('G')
			B = self.get_band_index('B')
			self.truecolImage = self.get_image((R,G,B),'RGB')
		return self.truecolImage
		
	def get_image(self, bands, colors='RGB'):
		'''Returns a viewable image, associating each band to a color.
		Bands can be eg: (1,2,3). Colors determines if image is
		RGB or grey-scale.'''
		row,col = self.size
		photo 	= Tkinter.PhotoImage(width=col, height=row)
		if colors == 'RGB':
			
			R = self.band[bands[0]]
			G = self.band[bands[1]]
			B = self.band[bands[2]]
			
			# Normalize vectors in [0-255]
			R = normalize_matrix(R)
			G = normalize_matrix(G)
			B = normalize_matrix(B)
			
			# Fill image
			for j in xrange(row):
				for i in xrange(col):
					put_pixel(photo, (R[j,i], G[j,i], B[j,i]), (i,j))
		elif colors == 'Grey':
			print colors,'not supported yet.'
		return self.resize_image(photo)
	
	def get_ibi_image(self, **kwargs):
		'''Calculates IBI index and returns a
		grey-scale image representing it.'''
		N = self.ibi = self.calc_ibi(**kwargs)
		row, col = self.size
		photo 	= Tkinter.PhotoImage(width=col, height=row)
		
		# Set to 0 entries < 0. This should
		# increase the contrast
		zeros = N < 0
		for j in xrange(row):
			for i in xrange(col):
				if zeros[j,i]:
					N[j,i] = 0				
		N = normalize_matrix(N)
		for j in xrange(row):
			for i in xrange(col):
				put_pixel(photo, N[j][i], (i,j))
		return self.resize_image(photo)
	
	def get_ibi_t_image(self, T, color_0=(0,0,0), color_1=(255,255,255)):
		'''Thresholds IBI with T and returns an image.
		It allows to choose a color for both the thresholded
		IBI values (0,1)'''
		N = self.ibi_t = self.threshold_ibi(T)
		row, col = self.size
		photo 	= Tkinter.PhotoImage(width=col, height=row)
		# ibi_t is yet normalized
		for j in xrange(row):
			for i in xrange(col):
				if N[j][i] == 0:
					put_pixel(photo, color_0, (i,j))
				else:
					put_pixel(photo, color_1, (i,j))
		return self.resize_image(photo)

	def change_band_name(self, index, name):
		#self.require_bands([index])
		self.meta['band names'][index] = name

	def get_band_index(self, band):
		'''Returns the index associated to the
		freq band "band". Returns -1 if not
		defined. It is preferable to check if
		band is defined with self.require_bands()
		before calling this function.'''
		try:
			return self.meta['band names'].index(band.upper())
		except:
			return -1
	
	def get_ibi_max_value(self):
		'''Returns the max value in IBI.'''
		self.require_bands(['IBI'])
		IBI = self.band[self.get_band_index('IBI')]
		return numpy.amax(IBI)
	
	def get_ibi_min_value(self):
		'''Returns the min value in IBI.'''
		self.require_bands(['IBI'])
		IBI = self.band[self.get_band_index('IBI')]
		return numpy.amin(IBI)
	
	def get_ibi_values(self):
		'''Returns a vector containing all entries
		of IBI.'''
		self.require_bands(['IBI'])
		IBI = self.band[self.get_band_index('IBI')]
		return numpy.concatenate(IBI)
	
	def new_band(self,band, bandName):
		if (len(band),len(band[0])) == self.size:
			self.meta['band names'].append(bandName)
			self.band[self.nbands]=band
			self.nbands = self.nbands + 1
		else:
			print 'Band cannot be inserted: dimensions do not match'
	
	def save_image(self, fn):
		row,col = self.size
		img = numpy.zeros((row,col,self.nbands))
		for b in xrange(self.nbands):
			for i in xrange(row):
				for j in xrange(col):
					img[i,j,b] = self.band[b][i,j]
		spectral.envi.save_image(fn,img,force=True,metadata=self.meta)
			
	def require_bands(self, bands):
		'''Check if bands (bands names) are
		defined. Raises exception in case they're
		not.'''
		for b in bands:
			if self.get_band_index(b) == -1:
				raise Exception('Missing band',b)
		return True
	
	# Next functions operate on bands, calculating indexes.
	#
	def calc_ibi(self, **kwargs):
		'''_type: specifies if the IBI is to be calculated
		using "SAVI" or "NDVI" index. If "SAVI" case a
		parameter l is to be specified, according to the
		vegetation presence. Values for l are in [0-1]
		range.'''
		if kwargs['_type'] == 'SAVI':
			l = kwargs['l']
			NDBI  = self.calc_ndbi()
			SAVI  = self.calc_savi(l)
			MNDWI = self.calc_mndwi()
			NDBI  = (NDBI + abs(numpy.amin(NDBI)))*255/numpy.amax(NDBI + abs(numpy.amin(NDBI)))
			SAVI  = (SAVI + abs(numpy.amin(SAVI)))*255/numpy.amax(SAVI + abs(numpy.amin(SAVI)))
			MNDWI  = (MNDWI + abs(numpy.amin(MNDWI)))*255/numpy.amax(MNDWI + abs(numpy.amin(MNDWI)))
			IBI = (NDBI-(SAVI+MNDWI)/2)/(NDBI+(SAVI+MNDWI))
		elif kwargs['_type'] == 'NDVI':
			self.require_bands(['MIR','NIR','R','G'])
			NDVI = self.calc_ndvi()
			MIR  = self.band[self.get_band_index('MIR')]
			NIR  = self.band[self.get_band_index('NIR')]
			R	 = self.band[self.get_band_index('R')]
			G	 = self.band[self.get_band_index('G')]
			IBI = (2*MIR/(MIR+NIR)-(NIR/(NIR+R)+G/(G+MIR)))/(2*MIR/(MIR+NIR)+(NIR/(NIR+R)+G/(G+MIR)))
		else:
			return
		# Create a new band containing IBI
		i = self.get_band_index('IBI')
		if i==-1:
			self.new_band(IBI,'IBI')
		else:
			self.band[i]=IBI
		return IBI

	def calc_mndwi(self):
		self.require_bands(['G','MIR'])
		G = self.band[self.get_band_index('G')]
		MIR = self.band[self.get_band_index('MIR')]
		MNDWI = (G-MIR)/(G+MIR)
		return MNDWI

	def calc_ndbi(self):
		self.require_bands(['NIR','MIR'])
		NIR = self.band[self.get_band_index('NIR')]
		MIR = self.band[self.get_band_index('MIR')]
		NDBI = (MIR-NIR)/(MIR+NIR)
		return NDBI

	def calc_ndvi(self):
		self.require_bands(['R','NIR'])
		R_idx 	= self.get_band_index('R')
		NIR_idx = self.get_band_index('NIR')
		NDVI = spectral.ndvi(self.img, R_idx, NIR_idx)	
		return NDVI
	
	def calc_savi(self, l):
		self.require_bands(['NIR','R'])
		NIR = self.band[self.get_band_index('NIR')]
		R = self.band[self.get_band_index('R')]
		SAVI = (NIR-R)*(1+l)/(NIR+R+l)
		return SAVI
	
	def threshold_ibi(self, T):
		'''Returns a matrix composed by zeros or
		ones where IBI is lower/greater than T. '''
		self.require_bands(['IBI'])
		ones  = 255
		zeros = 0
		IBI = self.band[self.get_band_index('IBI')]
		IBI_T = IBI.copy()
		IBI_T[(IBI_T>=T)] = ones
		IBI_T[(IBI_T<T)]  = zeros
		# Create a new band containing IBI_T
		i = self.get_band_index('IBI_T')
		if i==-1:
			self.new_band(IBI_T,'IBI_T')
		else:
			self.band[i]=IBI_T
		return IBI_T
