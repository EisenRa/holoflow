 #13.05.2020 - Holoflow 0.1.

import subprocess
import argparse
import os
import time


#Argument parsing
parser = argparse.ArgumentParser(description='Runs holoflow pipeline.')
parser.add_argument('-a', help="assembly file", dest="a", required=True)
parser.add_argument('-1', help="read1", dest="read1", required=True)
parser.add_argument('-2', help="read2", dest="read2", required=True)
parser.add_argument('-t', help="threads", dest="t", required=True)
parser.add_argument('-obam', help="output bam file", dest="obam", required=True)
parser.add_argument('-ID', help="ID", dest="ID", required=True)
parser.add_argument('-log', help="pipeline log file", dest="log", required=True)
args = parser.parse_args()


a=args.a
read1=args.read1
read2=args.read2
t=args.t
obam=args.obam
ID=args.ID
log=args.log



# Run

# Write to log
current_time = time.strftime("%m.%d.%y %H:%M", time.localtime())
with open(str(log),'a+') as log:
    log.write('\t\t'+current_time+'\tAssembly Mapping step - '+ID+'\n')
    log.write('The original metagenomic reads are being mapped to the indexed assembly so coverage info can be retrieved.\n\n')

# if output bam does not exist, continue
if not os.path.isfile(obam):

    unzCmd='gunzip '+a+' '+read1+' '+read2+''
    subprocess.check_call(unzCmd, shell=True)
    a = a.replace('.gz','')
    read1 = read1.replace('.gz','')
    read2 = read2.replace('.gz','')

    # map metagenomic reads to assembly to retrieve contigs' depth info for binning later
    mappingCmd='module load tools samtools/1.11 bwa/0.7.15 && bwa mem -t '+t+' -R "@RG\tID:ProjectName\tCN:AuthorName\tDS:Mappingt\tPL:Illumina1.9\tSM:ID" '+a+' '+read1+' '+read2+' | samtools view -b - | samtools sort -T '+obam+'.'+ID+' -o '+obam+''
    subprocess.Popen(mappingCmd, shell=True).wait()
