"""
Analyze NRES pipline data for S/N.

This is an umbrella script to crawkl through directories of nres reduced data. For each  reduced spectrum, S/N will
 be extracted from pipeline report. a target identifier will be looked up via simbad to query the target's V magnitude.

 A summary plot of exposure time normalized S/N vs. target magnitude is produced in the end as  success metric for observations.

"""
import argparse

import numpy as np
import matplotlib.pyplot as plt
import dateutil.parser
import nres_snanalysis as nres
import logging

def initplotting ():
    plt.rcParams["figure.figsize"] = (10,6)
    from matplotlib import style
    plt.style.use('ggplot')


def crawlSNbyInstrAndDates(instruments, args):
    global site, instrument, date
    for site, instrument in instruments:

        for date in (args.date):
            print
            site, instrument, date
            nres.crawldata(site, instrument, date, args.perdiem)




def plot_bydayandinstrumnet(instruments, args):
    global site, instrument, date
    # Do the fancy plotting
    fig, ax = plt.subplots(1)
    for site, instrument in instruments:

        for date in (args.date):
            print (args.perdiem, instrument, date)
            nres.plotfile('%s/%s-%s.txt' % (args.perdiem,instrument, date), color='red' if site == 'elp' else 'blue',
                          label='%s %s %s' % (site, instrument, date),
                          refflux=0)

    # Reference throughput
    nres.plotfile(None, color='gray',  label='lsc nres01 pre-fl10', refflux=   500000, ron=args.ron)
    nres.plotfile(None, color='blue',  label='lsc nres01',          refflux=   180000, ron=args.ron)
    nres.plotfile(None, color='red',   label='elp nres02',          refflux=   900000, ron=args.ron)
    nres.plotfile(None, color='lightgreen', label='NASA req',       refflux=  4180030, ron=0.001)
    nres.plotfile(None, color='brown', label='NSF promise',         refflux= 10499761, ron=0.001)

    # prettyfication
    lgd = plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1, fontsize=15)
    plt.xlim([1, 15])
    plt.xlabel("\nV mag", fontsize=20)
    plt.ylabel("S/N\n", fontsize=20)
    plt.title("NRES S/N model\n per resolution element for 60 sec exposure, 5100 Ang\n", fontsize=20)
    ax.grid(b=True, which='major', color='k', linestyle='-')
    ax.grid(b=True, which='minor', color='k', linestyle='--')
    ax.tick_params(axis='both', which='major', labelsize=15)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    plt.subplots_adjust(top=0.88)

    if args.plotname is not None:
        plt.savefig(args.plotname, box_extra_artists=(lgd,), bbox_inches="tight");
    else:
        print ("Not plotting!")



def parseCommandLine():
    """ Read command line parameters
    """

    parser = argparse.ArgumentParser(
        description='Crawl NRES pipeline to measure throughput and acqusition efficiency.')
    parser.add_argument('--log_level', dest='log_level', default='INFO', choices=['DEBUG', 'INFO'],
                        help='Set the debug level')
    parser.add_argument('--perdiems', dest='perdiem', default='../perdiem',
                        help='Directory containing photometryc databases')
    parser.add_argument('--instruments', dest='instruments', nargs='+', default = "nres01 nres02",  choices=['nres01', 'nres02', 'nres03'],  help='sites code for camera')
    parser.add_argument('--date', default='20171128', nargs= '+' , help='UTC start of night date')
    parser.add_argument('--plotname', default = 'NRESsn.png')
    parser.add_argument('--ron', default = 0)
    parser.add_argument('--crawl', action='store_true', help="Crawl through archive to extract S/N")
    parser.add_argument('--plot', action='store_true', help="Plot S/N for time frame")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(asctime)s.%(msecs).03d %(levelname)7s: %(module)20s: %(message)s')
    return args


instruments = [
    ('lsc', 'nres01'),
    ('elp', 'nres02'),
]

perdiemprefix = "../perdiem"

if __name__ == '__main__':

    args = parseCommandLine()

    # process which instruemnts to parse
    myinstruments = []
    for (s,i) in instruments:
        if i in args.instruments:
            myinstruments.append([s,i])

    # process which dates to parse & print
    if args.date is  None:
        exit (1)

    if args.crawl:
        print ("Crawling pipeline reports...")
        crawlSNbyInstrAndDates(myinstruments,  args)
        print ("Done.")
    if args.plot:
        print ("Plotting S/N summary")
        initplotting()
        plot_bydayandinstrumnet( myinstruments, args)
        print ("Done")