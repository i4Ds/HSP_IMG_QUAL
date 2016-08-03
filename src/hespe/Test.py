'''
Created on 22.07.2016

@author: Kushtrim Sylejmani
'''

import astropy
import numpy as np
import collections
from astropy.io import fits

print "Hello World!"
print "Open Fits file"
hdulist = fits.open('files/Erster_hsp_6120421_26454/coarse/11_20061204.142845_131_bpmap_photon.fits')
hdulistA = fits.open('files/Erster_hsp_6120421_26454/coarse/11_20061204.142917_131_bpmap_photon.fits')
hdulistB = fits.open('files/Erster_hsp_6120421_26454/coarse/5_20061204.145546_131_bpmap_photon.fits')

print "Opened FITS file\n"

print "#=========================================================#"
print "# General functions"
print "#=========================================================#"

print "HDUList info:"
hdulist.info()

print "\nHead:"
#===============================================================================
# print hdulist[0].[27]
#===============================================================================


print "\nSet new data in Header"
prihdr = hdulist[0].header
prihdr['targname'] = ('NGC121-a', 'the observation target')
prihdr[27] = 99
print prihdr[27]
print prihdr['targname']
print prihdr.comments['targname']

print 'Set new comment'
prihdr['comment'] = 'This is the first comment.'
print prihdr['comment']

print 'Add new comment'
prihdr['comment'] = 'This is the second comment.'
print prihdr['comment']

prihdr.set('observer', 'Edwin Hubble')

print "\n"
print "#=========================================================#"
print " Content of the Header 1:"
print "#=========================================================#"
print repr(hdulist[0].header)

print "\n"
print "#=========================================================#"
print " Content of the Header 2:"
print "#=========================================================#"
print repr(hdulistA[0].header)

print "\n"
print "#=========================================================#"
print " Content of the Header 3:"
print "#=========================================================#"
print repr(hdulistB[0].header)


print "\r\n\nKeys of the Header:"
print hdulist[0].header.keys()


print "\n"
print "#=========================================================#"
print "# Image Data"
print "#=========================================================#"

print "Data from hdulist"
scidata = hdulist[1].data
print scidata


#===============================================================================
# scidata = hdulist['ENERGY_L'].data
# print scidata
#===============================================================================

print "SciData Shape:"
print scidata.shape

print "\nSciData Dtype Name:"
print scidata.dtype.name


print "Columns"
cols = hdulist[1].columns
print "Columns Info:"
cols.info()

print "\n"
print "Column Names:"
cols.names


print "\n"
print "#=========================================================#"
print "# Create new a New Image File"
print "#=========================================================#"

#===============================================================================
# a simple sequence of floats from 0.0 to 99.9
#===============================================================================

n = np.arange(100.0)

#===============================================================================
# Create a PrimaryHDU object to encapsulate the data
#===============================================================================
hdu = fits.PrimaryHDU(n)

#===============================================================================
# Create a HDUList to contain the newly created primary HDU
#===============================================================================

hdulist = fits.HDUList([hdu])
#===============================================================================
# hdulist.writeto("new.fits")
#===============================================================================

print "\n"
print "#=========================================================#"
print "# Python Hashmap"
print "#=========================================================#"
d= {'key':'value'}
print d

print "\n new Key and Value:"
d['mynewkey'] = 'mynewvalue'
print d

print "\n"
print "#=========================================================#"
print "# Python Hashmap: Sort by Key 'OrderDict (collections)'"
print "#=========================================================#"
od = collections.OrderedDict(sorted(d.items()))
print od


print "\n"
print "#=========================================================#"
print "# FITS files closed"
print "#=========================================================#"
hdulist.close()
