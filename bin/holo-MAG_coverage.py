#22.11.2020 - Holoflow 0.1.

import subprocess
import argparse
import os
import glob
import numpy as np
import time


#Argument parsing
parser = argparse.ArgumentParser(description='Runs holoflow pipeline.')
parser.add_argument('-bam_dir', help="input bam from mapped MAGs to .fastq directory", dest="bam_dir", required=True)
parser.add_argument('-mag_dir', help="originally dereplicated mags", dest="mag_dir", required=True)
parser.add_argument('-out_dir', help="main output directory", dest="out_dir", required=True)
parser.add_argument('-ID', help="ID", dest="ID", required=True)
parser.add_argument('-log', help="pipeline log file", dest="log", required=True)
parser.add_argument('-t', help="threads", dest="threads", required=True)
args = parser.parse_args()

bam_dir=args.bam_dir
mag_dir=args.mag_dir
out_dir=args.out_dir
ID=args.ID
log=args.log
threads=args.threads

# Run


# Write to log
current_time = time.strftime("%m.%d.%y %H:%M", time.localtime())
with open(str(log),'a+') as logi:
    logi.write('\t\t'+current_time+'\tMAG Coverage step - '+ID+'\n')
    logi.write('\tTwo tables are generated respectively depicting the coverage of every MAG and of every contig in it for every sample.')

# # Extract MAGs coverage from bam files - BY CONTIG
#     # CONTIGS X SAMPLES
out_dir = out_dir+'/'+ID
depth_contig=out_dir+'/'+ID+'.coverage_byContig.txt'
if not (os.path.isfile(depth_contig)):
    getcoverageCmd='module unload gcc && module load tools perl/5.20.2 metabat/2.12.1 && jgi_summarize_bam_contig_depths --outputDepth '+depth_contig+' '+str(bam_dir)+'/*.bam'
    subprocess.check_call(getcoverageCmd, shell=True)
else:
    pass

# Generate aggregated coverage table  - BY MAG
    # MAGS X SAMPLES
depth_mag=out_dir+'/'+ID+'.coverage_byMAG.txt'
coverage_data=list()

with open(depth_mag, 'w+') as cov_mag:

    # Start MAG table with same line as depth_mag
    cov_contig = open(depth_contig,'r')
    first_dcontig = cov_contig.readline()
    first_dcontig = first_dcontig.replace('contig','MAG')
    # Generate header of new MAG coverage file: contigID, contigLength, averageCoverage + .bam coverage
    first_dMAG = '\t'.join(first_dcontig.split()[0:3])
    first_dMAG += '\t'+'\t'.join(sorted([os.path.basename(x) for x in glob.glob(bam_dir+'/*.bam')]))
    cov_mag.write(first_dMAG.strip()+'\n')
    cov_contig.close()


    # Prepare mag data and ID
    mag_list=glob.glob(str(mag_dir)+'/*.fa')
    for mag in mag_list:
        mag_id=''
        cov_data_tomag=''
        mag_id=os.path.basename(mag)
        mag_id=mag_id.replace('.fa','')
        if '.contigs' in mag_id:
            mag_id=mag_id.replace('.contigs','')

        # Generate tmp file with contig data from given MAG
        tmp_MAGcoverage=out_dir+'/'+ID+'.'+mag_id+'_MAGcoverage.txt_tmp'

        cmd='grep '+mag_id+' '+depth_contig+' > '+tmp_MAGcoverage+''
        subprocess.Popen(cmd,shell=True).wait()


        # Define array which contains contigLength in first column and coverage data in the rest
        cov_data_id=np.genfromtxt(tmp_MAGcoverage,delimiter='\t')
        cov_data_id=np.array(cov_data_id)
        cov_data = np.delete(cov_data_id, obj=0, axis=1) # remove contig ID column in array

        # Define contig lengths
        contig_Len=cov_data[:,0]
        # Define coverages matrix
        coverageS=cov_data[:,::2] # get even columns (.bam$)
        coverageS = np.delete(coverageS, obj=0, axis=1) # Remove contig length column
            # Insert total avg coverage
        avg_coverageS=cov_data[:,1]
        coverageS = np.insert(coverageS, 0, avg_coverageS, axis=1)


        # Vector with MAG length
        MAG_Len=np.sum(contig_Len,axis=0)
        # Get MAG coverage
            #Multiply coverageS for every contig to its Length
        MAG_coverages=coverageS*contig_Len[:,np.newaxis]
            #Sum all contig (coverages*length) in that MAG for given sample
        MAG_coverages=np.sum(MAG_coverages,axis=0)
            # Divide by MAG length to normalize
        MAG_coverages=MAG_coverages/MAG_Len


        # Generate new array with final data --> list
        MAG_array= np.insert(MAG_coverages, 0, MAG_Len)
        MAG_array=MAG_array.round(decimals=4)
        MAG_list=MAG_array.tolist()


        # Write coverage for given MAG in file
        for num in MAG_list:
            cov_data_tomag+=str(num)+'\t'

        cov_mag.write(mag_id+'\t'+str(cov_data_tomag)+'\n')
        os.remove(tmp_MAGcoverage)
