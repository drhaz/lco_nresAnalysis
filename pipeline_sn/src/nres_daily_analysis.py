"""
Analyze NRES pipline data for S/N.

This is an umbrella script to crawkl through directories of nres reduced data. For each  reduced spectrum, S/N will
 be extracted from pipeline report. a target identifier will be looked up via simbad to query the target's V magnitude.

 A summary plot of exposure time normalized S/N vs. target magnitude is produced in the end as  success metric for observations.

"""
import matplotlib
matplotlib.use("Agg")
import argparse

import matplotlib.pyplot as plt
import datetime as dt
import nres_snanalysis as nres
import logging


# Known nres instruments and locations
instruments = [
    ('lsc', 'nres01'),
    ('elp', 'nres02'),
    ('cpt', 'nres03')
]

def initplotting ():
    plt.rcParams["figure.figsize"] = (10,6)
    plt.style.use('ggplot')


def crawlSNbyInstrAndDates(instruments, args):
    """
    Wrapper funtion do call crawling S/N from PDF for a given night.

    :param instruments:
    :param args:
    :return:
    """

    #global site, instrument, date
    for site, instrument in instruments:

        for date in (args.date):
            print (site, instrument, date)
            nres.crawldata(site, instrument, date, args.perdiem)




def plot_bydayandinstrumnet(instruments, args):
    """
    Searches for buffered S/N data for range of date, instruments, and make a niceh S/N plot

    :param instruments:
    :param args:
    :return:
    """

    # Do the fancy plotting
    fig, ax = plt.subplots(1)
    for site, instrument in instruments:

        if site == 'elp':
            color = 'red'
        if site == 'lsc':
            color = 'blue'
        if site == 'cpt':
            color = 'green'

        for date in (args.date):

            nres.plotfile('%s/%s-%s.txt' % (args.perdiem,instrument, date), color=color,
                          label='%s %s %s' % (site, instrument, date),
                          refflux=0)

    # Reference throughput
    nres.plotfile(None, color='gray',  label='lsc nres01 pre-fl10',         refflux=    500000, ron=args.ron)
    nres.plotfile(None, color='blue',  label='lsc nres01',                  refflux=    180000, ron=args.ron)
    nres.plotfile(None, color='red',   label='elp nres02',                  refflux=    900000, ron=args.ron)
    # Assumption: S/N= 10 for 20 min on V=12 start (NSF proposal)
    # hence S/N (Texp=60, V=12) = 10 * sqrt (6.3) / sqrt (20) = 5.6,
    nres.plotfile(None, color='green', label='NSF promise revised',         refflux=   1978682, ron=0.001)
    #nres.plotfile(None, color='brown', label='NSF promise (wrong)',         refflux=  10499761, ron=0.001)
    # Trickier, worst case: S/N=100 to reach 3m/s for V=12 mag in 60 minutes
    # S/N (t=60 sec) = 100 /sqrt (60) = 12.9
    nres.plotfile(None, color='cyan', label='TESS classification',          refflux=  995267, ron=0.001)
    # Trickier, worst case: S/N=100 to reach 3m/s for V=12 mag in 60 minutes
    # S/N (t=60 sec) = 0 /sqrt (60) = 12.9
    #nres.plotfile(None, color='cyan', label='S/N=100 1h V=12 3m/s',         refflux=  1682552, ron=0.001)

    # prettyfication
    lgd = plt.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1, fontsize=15)
    plt.xlim([0, 15])
    plt.xlabel("\nV mag", fontsize=20)
    plt.ylabel("S/N\n", fontsize=20)
    plt.title("NRES S/N model\n per resolution element for 60 sec exposure, 5100 Ang\n", fontsize=20)
    ax.grid(b=True, which='major', color='k', linestyle='-')
    ax.grid(b=True, which='minor', color='k', linestyle='--')
    ax.tick_params(axis='both', which='major', labelsize=15)
    ax.tick_params(axis='both', which='minor', labelsize=10)
    plt.subplots_adjust(top=0.88)

    if args.plotname is not None:
        import cStringIO
        from PIL import Image
        ram = cStringIO.StringIO()
        plt.savefig(ram, box_extra_artists=(lgd,), bbox_inches="tight", dpi=400);
        ram.seek(0)
        im = Image.open(ram)
        im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
        im2.save( args.plotname , format='PNG')
    else:
        print ("Not plotting!")



def parseCommandLine():
    """ Read command line parameters
    """

    todaydefault = dt.datetime.utcnow().date() - dt.timedelta( days = 1)
    todaydefault = todaydefault.strftime("%Y%m%d")
    parser = argparse.ArgumentParser(
        description='Crawl NRES pipeline to measure throughput and acqusition efficiency.')
    parser.add_argument('--log_level', dest='log_level', default='INFO', choices=['DEBUG', 'INFO'],
                        help='Set the debug level')
    parser.add_argument('--perdiems', dest='perdiem', default='../perdiem',
                        help='Directory containing photometryc databases')
    parser.add_argument('--instruments', dest='instruments', nargs='+', default = "nres01 nres02 nres03",  choices=['nres01', 'nres02', 'nres03'],  help='sites code for camera')
    parser.add_argument('--date', default=[todaydefault,], nargs= '+' , help='UTC start of night date')
    parser.add_argument('--plotname', default = 'NRESsn.png')
    parser.add_argument('--ron', default = 0)
    parser.add_argument('--crawl', action='store_true', help="Crawl through archive to extract S/N")
    parser.add_argument('--plot', action='store_true', help="Plot S/N for time frame")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format='%(asctime)s.%(msecs).03d %(levelname)7s: %(module)20s: %(message)s')

    return args





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
