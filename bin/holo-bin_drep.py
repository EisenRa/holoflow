#03.09.2020 - Holoflow 0.1.

import subprocess
import argparse
import os
import glob
import time


#Argument parsing
parser = argparse.ArgumentParser(description='Runs holoflow pipeline.')
parser.add_argument('-dt_bd', help="dastool bin directory", dest="dt_bd", required=True)
parser.add_argument('-out_dir', help="main output directory", dest="out_dir", required=True)
parser.add_argument('-sample', help="sample", dest="sample", required=True)
parser.add_argument('-log', help="pipeline log file", dest="log", required=True)
parser.add_argument('-t', help="threads", dest="threads", required=True)
args = parser.parse_args()



dt_bd=args.dt_bd
out_dir=args.out_dir
sample=args.sample
log=args.log
threads=args.threads


# Run
if not (os.path.exists(str(out_dir))):
    os.mkdir(str(out_dir))
    os.mkdir(str(out_dir+'/'+sample))
    out_dir = str(out_dir+'/'+sample)

    # Write to log
    current_time = time.strftime("%m.%d.%y %H:%M", time.localtime())
    with open(str(log),'a+') as logi:
        logi.write('\t\t'+current_time+'\t step - Sample '+sample+'\n')
        logi.write(' \n\n')


    # Get genomeInfo from Dastool
    # Recover completeness and redundancy from Bin Merging Summary

    # Save all bin_path,completeness,redundancy in new .csv file
    binlist = glob.glob(str(dt_bd)+"*.fa")
    with open(str(''+out_dir+'/final_bins_Info.csv'),'w+') as bins:
        # open binmergingsummary file
        with open(str(''+dt_bd+'/../'+sample+'_DASTool_summary.txt'),'r') as summary:
            for i in range(len(summary)):
                if summary[i].startswith(str(sample)):
                    line_data = summary[i].split()
                    completeness = line_data[10]
                    redundancy = line_data[11]
                    bins.write(os.path.abspath(binlist[i])+','+completeness+','+redundancy+'\n')
                else:
                    pass



    drepbinsCmd='dRep dereplicate '+out_dir+' -p '+threads+' -g '+dt_bd+'/*.fa --genomeInfo '+out_dir+'/final_bins_Info.csv'
    subprocess.check_call(drepbinsCmd, shell=True)


    # Write to log
    current_time = time.strftime("%m.%d.%y %H:%M", time.localtime())
    with open(str(log),'a+') as logf:
        logf.write(''+current_time+' - \n\n')