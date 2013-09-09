#!/usr/bin/python
###############
#             #
#############################
# File:   gui.py			#
# Author: Giovanni Cherubin	#
import images_util
import tkFileDialog
import spectral
from Tkinter import *

class CustomMenu:
	def __init__(self, master, ctrl):
		self.master = master
		self.ctrl = ctrl
		self.menubar = self.init_menu()

	def init_menu(self):
		# Menu: Help, Quit
		menubar = Menu(self.master)
		menubar.add_command(label="Help", command=self.noop)
		menubar.add_command(label="Quit", 
							command=self.master.quit)
		
		# Menu: File->(Load,Save)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Apri un file...",
							command=self.ctrl.load_image)
		filemenu.add_command(label="Salva...",
							command=self.ctrl.save_results)
		filemenu.add_command(label="Salva l'immagine visualizzata...",
							command=self.ctrl.save_shown_image)
		#filemenu.add_separator()
		menubar.add_cascade(label="File", menu=filemenu)
		
		# Menu: View->(Img colors,Show master img,Show res)
		viewmenu = Menu(menubar, tearoff=0)
		self.cb1 = BooleanVar()
		self.cb2 = BooleanVar()
		self.cb3 = BooleanVar()
		viewmenu.add_checkbutton(label="Visualizza l'immagine principale", 
							command=lambda: 
									self.ctrl.show_image('main', self.cb1.get()),
							onvalue=True,
							offvalue=False,
							variable=self.cb1)
		viewmenu.add_checkbutton(label="Visualizza l'IBI", 
							command=lambda:
									self.ctrl.show_image('res', self.cb2.get()),
							onvalue=True,
							offvalue=False,
							variable=self.cb2)
		viewmenu.add_checkbutton(label="Visualizza l'IBI sogliato", 
							command=lambda:
									self.ctrl.show_image('thr', self.cb3.get()),
							onvalue=True,
							offvalue=False,
							variable=self.cb3)
		menubar.add_cascade(label="Vista", menu=viewmenu)
		
		# Menu: Indexes->(Calculate IBI)
		indexmenu = Menu(menubar, tearoff=0)
		indexmenu.add_command(label="IBI - Calcola indice",
							command=self.ctrl.calc_ibi)
		indexmenu.add_command(label="IBI - Soglia indice",
							command=self.ctrl.threshold_to_ibi)
		menubar.add_cascade(label="Strumenti", menu=indexmenu)
		
		self.master.config(menu=menubar)
		return menubar


	def set_checkbutton_state(self, checkb, state):
		if checkb == 'main':
			self.cb1.set(state)
		elif checkb == 'res':
			self.cb2.set(state)
		elif checkb == 'thr':
			self.cb3.set(state)


	def bind(self, evt, funct):
		self.menubar.bind(evt, funct)
	
	
	def noop(self):
		'''************'''
		pass
	
