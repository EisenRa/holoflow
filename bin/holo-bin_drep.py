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
parser.add_argument('-ID', help="ID", dest="ID", required=True)
parser.add_argument('-log', help="pipeline log file", dest="log", required=True)
parser.add_argument('-t', help="threads", dest="threads", required=True)
args = parser.parse_args()



dt_bd=args.dt_bd
out_dir=args.out_dir
ID=args.ID
log=args.log
threads=args.threads


# Run
if not (os.path.exists(str(out_dir))):
    os.mkdir(str(out_dir))

    # Write to log
    current_time = time.strftime("%m.%d.%y %H:%M", time.localtime())
    with open(str(log),'a+') as logi:
        logi.write('\t\t'+current_time+'\tBin Dereplication step - '+ID+'\n')
        logi.write('dRep identifies those bins that are technically the same  and removed all but the “best” one from each\nredundant set. This is done based on the Average Nucleotide Identity (ANI).\n\n')

    # Get genomeInfo from Dastool
    # Recover completeness and redundancy from Bin Merging Summary

    # Save all bin_path,completeness,redundancy in new .csv file
    with open(str(''+out_dir+'/final_bins_Info.csv'),'w+') as bin_data:
        bin_data.write('genome,completeness,contamination\n')

        stats_list=glob.glob(str(dt_bd)+"/*_DASTool_summary.txt")
        for file in stats_list:
            with open(str(file),'r') as summary:
                summary_data=summary.readlines()
                for line in summary_data:
                    if not (line.startswith('bin')):
                        line_data = line.split()
                        # store compl and red values in variables
                        bin_name = line_data[0]
                        completeness = line_data[11]
                        redundancy = line_data[12]

                        bin_data.write(os.path.abspath(bin_name+'.fa')+','+completeness+','+redundancy+'\n')
                    else:
                        pass

    # Rename bins to match DasTool summary data if they don't
    bin_list=glob.glob(str(dt_bd)+"/*.fa")
    for bin in bin_list:
        if 'contigs' in bin:
            new_bin=bin.replace('.contigs','')
             mvcmd='mv '+bin+' '+new_bin+''
             subprocess.check_call(mvcmd,shell=True)




    if (os.path.exists(str(''+out_dir+'/final_bins_Info.csv'))):
        drepbinsCmd='module load tools ngs anaconda2/4.4.0 pplacer/1.1.alpha19 anaconda3/4.4.0  mash/2.0 mummer/3.23 prodigal/2.6.3 centrifuge/1.0.3-beta hmmer/3.2.1 && dRep dereplicate '+out_dir+' -p '+threads+' -g '+dt_bd+'/*.fa --genomeInfo '+out_dir+'/final_bins_Info.csv'
        subprocess.check_call(drepbinsCmd, shell=True)
