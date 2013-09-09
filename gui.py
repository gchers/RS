#!/usr/bin/python
###############
#             #
#############################
# File:   gui.py			#
# Author: Giovanni Cherubin	#
import custom_menu
import tkFileDialog
import tkMessageBox
from Tkinter import *


# NOTE: change icon-text http://www.jamesstroud.com/jamess-miscellaneous-how-tos/icons/tkinter-title-bar-icon

class Gui:
	
	_DIALOGS_WIDTH = 500

	def __init__(self, master, title, maxsize, ctrl):
		'''Init the Gui with its variables, creates a new frame
		and inits the menu bar.'''
		self.master = master 
		self.maxsize = maxsize
		self.frame = Frame(self.master)
		self.frame.pack()
		self.menu = custom_menu.CustomMenu(self.master, ctrl)
		self.master.title(title)

	def start(self):
		self.master.mainloop()

	def set_image(self, photo, pos=(0,0)):
		'''Sets photo as the main image.
		photo is an instance of PhotoImage.'''
		assert isinstance(photo, PhotoImage)
		try:
			self.mainImage.destroy()
		except:
			pass
		# Check size
		if photo.width() > self.maxsize[0]:
			w = self.maxsize[0]
		else:
			w = photo.width()
		if photo.height() > self.maxsize[1]:
			h = self.maxsize[1]
		else:
			h = photo.height()

		self.mainImage = Label(self.master, image=photo, width=w,height=h)
		self.mainImage.photo = photo 		# keep a reference of the image (http://effbot.org/tkinterbook/label.htm)
		self.mainImage.pack()
		self.start()
	
	def get_shown_image(self):
		'''Returns the image shown at the
		moment.'''
		return self.mainImage.photo
	
	def select_file_open(self, ftype):
		'''Select file for opening.'''
		return tkFileDialog.askopenfilename(parent=self.master,filetypes=[ftype])	
	
	def select_file_save(self):
		'''Select file for saving data.'''
		return tkFileDialog.asksaveasfilename(parent=self.master) 
	
	def show_error(self, text, title='Errore'):
		'''Shows an error message box.'''
		tkMessageBox.showerror(title, text)
	
	def show_msg(self, text, title='Info'):
		'''Shows an Info message.'''
		tkMessageBox.showinfo(title, text);

	def choose_bands(self, bands, nbands):
		'''For each of bands let the user
		choose one of nbands (needed bands).'''
		indexes = []
		for b in bands:
			indexes.append(self.choose_band(b,nbands))
		return indexes

	def choose_band(self, band, bands):
		'''band: a band name (eg ['R','G',...])
		which the application needs. Its value
		is to be chosen in "bands".
		bands: a list of the band names provided
		by the image header.
		The user has to associate the band to
		one of the bands.'''
		self.top = top = Toplevel(self.master)
		label = Label(top, wraplength=self._DIALOGS_WIDTH, text='Scegli la banda che corrisponde a \'' + band +'\'')
		label.pack()
		choice = StringVar(self.master)
		choice.set(bands[0])
		w = OptionMenu(self.top,choice, *bands)
		w.pack()
		bok = Button(self.top, text='Ok', command=lambda: self.top.destroy())
		bno = Button(self.top, text='Annulla', command=lambda: self.top.destroy())
		bok.pack(side=RIGHT)
		bno.pack(side=LEFT)
		self.master.wait_window(self.top)
		return bands.index(choice.get())
	
	def choose_ibi_type(self):
		'''Prompts the user a message, allowing
		him to choose between IBI calculated
		with SAVI or not.'''
		self.top = Toplevel(self.master)
		label0 = Label(self.top, wraplength=self._DIALOGS_WIDTH, text="Scegliere se calcolare l'IBI usando l'indice SAVI, che permette di sogliare in caso di scarsa presenza di vegetazione (circa il 15%), oppure l'NDVI, nel caso la copertura della vegetazione sia al di sopra del 30%.")
		label0.pack()
		# following '==' is a little trick for letting lambda
		# executing more functions
		c_savi = lambda: choice.set('SAVI') == self.top.destroy()
		c_ndvi = lambda: choice.set('NDVI') == self.top.destroy()
		choice = StringVar('')
		butt_savi = Button(self.top, text='SAVI', command=c_savi)
		butt_savi.pack()
		butt_ndvi = Button(self.top, text='NDVI', command=c_ndvi)
		butt_ndvi.pack()
		self.master.wait_window(self.top)
		return choice.get()
	
	def on_cursor_move_thres(self, x, values, descr, prev=''):
		'''Returns the percentage of values greater than
		x.'''
		descr.set(((values>=x).sum()*100/len(values)).astype('|S3')+'% dell\'immagine.')
	
	def choose_ibi_threshold(self, ibiMax, ibiMin, ibiValues):
		'''Let the user choose a threshold for
		IBI.'''
		self.top = Toplevel(self.master)
		label0 = Label(self.top,
						wraplength=self._DIALOGS_WIDTH,
						text="Selezionare un valore di threshold per sogliare l'indice IBI. Attualmente i valori dell'indice sono compresi tra " + ibiMin.astype('|S4') + " e " + ibiMax.astype('|S4'))
		label0.pack()
		descr = StringVar()
		var = DoubleVar()
		var.set(ibiMin)
		
		bar = Scale(self.top, 
					variable=var,
					from_=ibiMin, to=ibiMax,
					resolution=0.0001,
					showvalue='yes',
					orient='horizontal',
					command=lambda x: self.on_cursor_move_thres(var.get(),ibiValues,descr))
		bar.pack()
		butt_ok = Button(self.top,
						text='Ok',
						command=lambda:self.top.destroy())
		butt_ok.pack()
		label1 = Label(self.top, textvariable=descr)
		label1.pack()
		self.master.wait_window(self.top)
		return var.get()

	def on_cursor_move_savi(self,x,descr):
		'''Returns label's value correspondent to x.'''
		if x<=0.3:
			descr.set('Grande presenza di vegetazione')
		elif x<0.7:
			descr.set('Media presenza di vegetazione')
		else:
			descr.set('Bassa presenza di vegetazione')


	def choose_savi_threshold(self):
		'''This dialog box let the user choose
		a threshold for SAVI.'''
		self.top = Toplevel(self.master)
		label0 = Label(self.top,
						wraplength=self._DIALOGS_WIDTH,
						text="Selezionare il parametro di correzione l per il calcolo dell'indice SAVI. Questo parametro indica la presenza stimata di vegetazione nell'immagine.")
		label0.pack()
		descr = StringVar()
		var = DoubleVar()
		var.set(0)
		self.on_cursor_move_savi(var.get(),descr)
		
		bar = Scale(self.top, 
					variable=var,
					from_=0, to=1,
					resolution=0.1,
					showvalue='yes',
					orient='horizontal',
					command=lambda x: self.on_cursor_move_savi(var.get(),descr))
		bar.pack()
		butt_ok = Button(self.top,
						text='Ok',
						command=lambda:self.top.destroy())
		butt_ok.pack()
		label1 = Label(self.top, textvariable=descr)
		label1.pack()
		self.master.wait_window(self.top)
		return var.get()
	
