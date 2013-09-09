# README

## RUNNING THE APPLICATION
To launch RS, from terminal (in the main folder):

	$ python rs.py
	
You may now open a ENVI Header (.hdr) image, and calculate the IBI on it.

## REQUIREMENTS
* Python >= 2.7
* PIL python library. (http://www.pythonware.com/products/pil/).
* SPy python module (http://spectralpython.sourceforge.net/)

## TROUBLESHOOTING
### Installing PIL under OSX
To install PIL library under OSX follow these instructions, from terminal:

	curl -O -L http://effbot.org/downloads/Imaging-1.1.7.tar.gz
	# extract
	tar -xzf Imaging-1.1.7.tar.gz
	cd Imaging-1.1.7
	# build and install
	python setup.py build
	sudo python setup.py install
