# Generate a S/N vs. stellar magnitude report for NRES observations

This package will crawl through the outpu9t from the NRES pipline 
(must have a local mount of the LCO archive) and extracts, for each output
 spectrum, the star identifier and the pipeline-estimated S/N. The V magnitude will
be queried (astropy.query), and a plot is generated of Vmag vs. S/N for object.
  
  
Usage example:
 
<pre>
 cd src
 python nres_daily_analysis.py  --plot --crawl --date  20180109
</pre>


The crawling results will be stored by nres instance and date in ../perdiem. The outputplot will by default be NRESsn.png



Detailed usage paramters:

<pre>
python nres_daily_analysis.py  -h
usage: nres_daily_analysis.py [-h] [--log_level {DEBUG,INFO}]
                              [--perdiems PERDIEM]
                              [--instruments {nres01,nres02,nres03} [{nres01,nres02,nres03} ...]]
                              [--date DATE [DATE ...]] [--plotname PLOTNAME]
                              [--ron RON] [--crawl] [--plot]

Crawl NRES pipeline to measure throughput and acqusition efficiency.

optional arguments:
  -h, --help            show this help message and exit
  --log_level {DEBUG,INFO}
                        Set the debug level
  --perdiems PERDIEM    Directory containing photometryc databases
  --instruments {nres01,nres02,nres03} [{nres01,nres02,nres03} ...]
                        sites code for camera
  --date DATE [DATE ...]
                        UTC start of night date
  --plotname PLOTNAME
  --ron RON
  --crawl               Crawl through archive to extract S/N
  --plot                Plot S/N for time frame
</pre>