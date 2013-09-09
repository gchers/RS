#!/usr/bin/python
# -*- coding: utf-8 -*-
###############
#             #
#############################
# File:   gui.py			#
# Author: Giovanni Cherubin	#
import gui
import spectral
import images_util
import Tkinter

class RSApp:
	
	_MAX_IMAGE_SIZE = (800,600) 	# this is the max size of the window which containis an image

	def __init__(self):
		self.master = Tkinter.Tk()
		self.gui = gui.Gui(self.master, "RS for all", self._MAX_IMAGE_SIZE, self)
		self.rsImage = None
		self.images = {'main':{'image':None,'visible':False},
						'res':{'image':None,'visible':False},
						'thr':{'image':None,'visible':False}}
	
	
	def refresh(self):
		self.master.mainloop()
	
	
	def calc_ibi(self):
		self.require_image_open()
		ibi_t = self.gui.choose_ibi_type()	
		if ibi_t == 'SAVI':
			l = self.gui.choose_savi_threshold()
		else:
			l = False
		
		try:
			self.images['res']['image'] = self.rsImage.get_ibi_image(_type=ibi_t,l=l)
		except Exception as e:
			if len(e.args) == 2 and e.args[0] == 'Missing band':
				bandindexes = self.gui.choose_bands(e.args[1], self.rsImage.bandn)
				for i in bandindexes:
					if i != -1:
			  			self.rsImage.change_band_name(i,e.args[1])
			  			self.images['res']['image'] = self.rsImage.get_ibi_image()
			else:
				raise
				return
		self.images['main']['visible'] = False
		self.show_image('res')
	
	def threshold_to_ibi(self):
	    self.require_image_open('main')
	    self.require_image_open('res')
	    ibiMax = self.rsImage.get_ibi_max_value()
	    ibiMin = self.rsImage.get_ibi_min_value()
	    ibiVals = self.rsImage.get_ibi_values()
	    thres = self.gui.choose_ibi_threshold(ibiMax,ibiMin,ibiVals)
	    self.images['thr']['image'] = self.rsImage.get_ibi_t_image(thres, (0,0,0), (255,255,255))
	    self.images['main']['visible'] = False
	    self.images['res']['visible'] = False
	    self.show_image('thr')
	
	def require_image_open(self, imageRef='main'):
		if self.images[imageRef]['image'] == None:
			self.gui.show_error("Non è stato possibile eseguire l'operazione.")
			self.refresh_checkbuttons_state()
			raise Exception
	
	def load_image(self): 
		fn = self.gui.select_file_open(('ENVI Header files','*.hdr'))
		if not fn:
			return
		try:	    
			self.images = {'main':{'image':None,'visible':False},
			 				'res':{'image':None,'visible':False},
			 				'thr':{'image':None,'visible':False}}
			self.rsImage = images_util.RemoteSensingImage(fn,self._MAX_IMAGE_SIZE)
		except Exception as e:
			print e
			self.gui.show_error('File corrotto!')
			return
		try:
			#self.rsImage.require_bands(['R','G','B'])
			self.images['main']['image'] = self.rsImage.get_true_colors()
		except Exception as e:
			if len(e.args) == 2 and e.args[0] == 'Missing band':
				bandindexes = self.gui.choose_bands(e.args[1],self.rsImage.meta['band names'])
				for i in range(len(bandindexes)):
					if i != -1:
						self.rsImage.change_band_name(bandindexes[i],e.args[1][i])
				self.images['main']['image'] = self.rsImage.get_true_colors()
			else:
				raise	
		#self.refresh_checkbuttons_state()	
		self.show_image('main')
	

	def save_results(self):
		'''Saves in ENVI format the original image.
		If any results (which are put in a new band,
		they're present into the stored image.'''
		self.require_image_open()
		fn = self.gui.select_file_save()
		if not fn:
			return
		if not fn.endswith('.hdr'):
			fn = fn + '.hdr'
		self.rsImage.save_image(fn)
		self.gui.show_msg("I dati sono stati salvati con successo")
	
	def save_shown_image(self):
		'''Saves the current displayed image in
		a common image format.'''
		self.require_image_open()
		fn = self.gui.select_file_save()
		if not fn:
			return
		if not fn.endswith('.tiff'):
			fn = fn + '.tiff'
		try:
			photo = self.gui.get_shown_image()
			images_util.photoimage2image(photo).save(fn,format='tiff')
			self.gui.show_msg("L'immagine è stata salvata con successo")
		except Exception as e:
			self.gui.show_error("Errore nel salvataggio: l'immagine non è stata salvata")
	
	def show_image(self, imageRef, setvisible=True):
		'''Shows the image specified between:
		('main','res','thr').
		If both 'main' and 'thr' are visible,
		these are overlayed and shown together.'''
		self.require_image_open(imageRef)
		main = self.images['main']
		res  = self.images['res']
		thr  = self.images['thr']
		if not setvisible:
			img = None
			self.images[imageRef]['visible'] = False
			for im in self.images.iterkeys():
				if self.images[im]['visible']:
					img = self.images[im]['image']	
		elif ((imageRef == 'main') and (thr['visible'])) or ((imageRef == 'thr') and (main['visible'])):
				self.images['main']['visible'] = True
				self.images['res']['visible'] = False
				self.images['thr']['visible']  = True
				img = images_util.overlay_images(main['image'],thr['image'])
		else:
			self.images['main']['visible'] = False
			self.images['res']['visible']  = False
			self.images['thr']['visible']  = False
			self.images[imageRef]['visible'] = True
			img = self.images[imageRef]['image']
				
		self.refresh_checkbuttons_state()
		self.gui.set_image(img)
		self.refresh()
	
	def refresh_checkbuttons_state(self):
		for im in self.images.iterkeys():
			self.gui.menu.set_checkbutton_state(im,self.images[im]['visible'])



if __name__ == '__main__':
	app = RSApp()
	app.refresh()
