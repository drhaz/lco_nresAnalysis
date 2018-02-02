import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import glob
import tarfile
import tempfile
import os
import os.path
import PyPDF2
import re
import shutil
from astroquery.simbad import Simbad


def readdata (fname):
    " Read in a per night s/n dump"
    data = np.genfromtxt (fname, unpack=True, dtype=None, 
                          skip_footer=0, names=['star','vmag','sn','texp'],)

    sn60 = data['sn'] * np.sqrt (60. / data['texp'])
    idx = np.isfinite(data['vmag'])
    return data['star'][idx], data['vmag'][idx], sn60[idx]


def snmodel (s0=180000, ron=5):
    x = np.arange (0,14,0.5)
    s = (10 ** (-0.4 * x)) * s0
    sn = s / np.sqrt (s + 3 * ron ** 2)
    return x, sn

    

def plotfile (fname, color, label, refflux, ron=5, badcutoff=25000):
    if (fname is not None) and os.path.isfile(fname):
        if  (os.path.getsize(fname) > 10) :
            (star,v,sn) = readdata (fname)
            plt.semilogy (v,sn,'o', color=color, label=label)
            for (label, x, y) in zip(star,v,sn):
                plt.annotate (label, xy=(x, y), fontsize=1)
        else:
            print ("Cannot use file " , fname, os.path.isfile(fname))
        
    if refflux > 0:    
        (x,sn) = snmodel (refflux,ron)
        plt.semilogy (x,sn, color=color, label='model %s' % label)

objectTranslation = {
    'PSIPHE' : 'psi Phe',
    'MUCAS' : 'mu Cas',
    'KS18C14487' :'TYC 8856-529-1',
    'BD093070': 'BD-09 3070'
}

def crawldata (site, nres, date, perdiemprefix,  mountpoint='/nfs/archive/engineering', outputname = None):
    """
        Crawl through a nres calibrated files directory and 
        (i) extract tar.gz, 
        (ii) read pdf summary plot file and aprse target name, exposure time, s/n
        (iii) query sinbad for v magnitude
        (iv) write output to text file
    """
    
    searchterm = '%s/%s/%s/%s/specproc/*.tar.gz' % (mountpoint, site, nres, date)
    
    starnames = []
    starmags = []
    starsns = []
    starexptimes = []
    
    tgzs = glob.glob (searchterm)
    for tgz in tgzs[0:]:

        tmpdir=tempfile.mkdtemp()
        
        with tarfile.open (tgz) as tf:
            basename = os.path.basename(tgz)[0:-7]
            tf.extract ('{basename}/{basename}.pdf'.format(basename=basename), path=tmpdir )
            tf.close
        
        with open (os.path.join( tmpdir , '{basename}/{basename}.pdf'.format(basename=basename)), 'rb') as pdffile:
            
            # Read the text content from pdf file, deeply burried in the tar ball.
            pdfreader = pdfreader = PyPDF2.PdfFileReader (pdffile)
            text = pdfreader.getPage(0).extractText()
            pdffile.close()
            #shutil.rmtree(tmpdir)
            
            # parse the output with an easy to read regex.
            regex = '^([\w_\s\+-]+)\,\s.+expt\s?=\s?(\d+) s\,.+N=\s*(\d+\.\d+),'
            m = re.search (regex, text)
            if m is not None:
                
                starname = m.group(1)
                exptime  = m.group(2)
                sn       = m.group(3)
            else:
                print ("%s/%s pdf regex match failed" % (tmpdir, basename))
                print ("Input:\n%s\n%s" % (text, regex))
                continue
            #if starname.upper().endswith('_ENGR'):
            #    print ('Rejecting star %s as it was observed as engineering test' % (starname))
            #    continue   
            # Query SIMBAD for the stellar magnitude
            mag = 99
            try:
                customSimbad = Simbad()
                customSimbad.add_votable_fields('flux(V)')
                
                
                searchname = starname if '_' not in starname else starname[0:starname.find('_')]
                if searchname in objectTranslation:
                    searchname = objectTranslation[searchname]
                print ('Searching for %s -> %s' % (starname, searchname))
                result = customSimbad.query_object(searchname)
                mag = result['FLUX_V'][0]  
                mag = float(mag) 
            except Exception as e:
                print ("Query failed", e)
                mag = 0
                
            # Log, and add everything to internal storge
            starname = starname.replace (' ','_')
            print (basename, starname, mag, sn, exptime)
            starnames.append (starname)
            starsns.append (sn)
            starexptimes.append (exptime)
            starmags.append (mag)      
            
    # And finally, write everything out to a text file for future use. 
    
    if outputname is None:
        outputname = "%s/%s-%s.txt" % (perdiemprefix, nres,date)
    with open(outputname, "w+") as myfile:
        for ii in range (len (starnames)):
              myfile.write ('%s %s %s %s\n' %( starnames[ii], starmags[ii], starsns[ii], starexptimes[ii]) )  
        
