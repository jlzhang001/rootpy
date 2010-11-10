#!/usr/bin/env python

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-v","--verbose", action="store_true", dest="verbose",
                  help="verbose", default=False)
parser.add_option("--nproc", action="store", type="int", dest="nproc",
                  help="number of students", default=1)
parser.add_option("--nevents", action="store", type="int", dest="nevents",
                  help="number of events to process by each student", default=-1)
parser.add_option("--jes", action="store_true", dest="doJESsys",
                  help="recalculate affected variables at EM+JES", default=False)
parser.add_option("--grl", action="store", type="str", dest="grl",
                  help="good runs list", default=None)
parser.add_option('-p',"--periods", action="store", type="str", dest="periods",
                  help="data period", default=None)
(options, args) = parser.parse_args()

import sys
import os
import datasets
import ROOT
import glob
from TauProcessor import *
from rootpy.analysis.batch import Supervisor
from rootpy.ntuple import NtupleChain
from rootpy.datasets import *

if not os.environ.has_key('DATAROOT'):
    sys.exit("DATAROOT not defined!")
dataroot = os.environ['DATAROOT']


ROOT.gROOT.ProcessLine('.L dicts.C+')

if options.periods:
    options.periods = options.periods.split(',')

if len(args) == 0:
    print "No samples specified!"
    sys.exit(1)

data = []
if len(args) == 1:
    if args[0].lower() == 'all':
        args = []
        dirs = glob.glob(os.path.join(dataroot,'*'))
        for dir in dirs:
            if os.path.isfile(os.path.join(dir,'meta.xml')):
                args.append(os.path.basename(dir))

for sample in args:
    dataset = get_sample(sample,options.periods)
    if not dataset:
        print "FATAL: sample %s does not exist!"%sample
        sys.exit(1)
    print "processing %s..."%dataset.name
    data.append(dataset)

if options.nproc == 1:
    for dataset in data:
        student = TauProcessor(dataset.files, numEvents = options.nevents, doJESsys=options.doJESsys, grl=options.grl)
        student.coursework()
        while student.research(): pass
        student.defend()
else:
    supervisor = Supervisor(datasets=data,nstudents=options.nproc,process=TauProcessor,nevents=options.nevents,verbose=options.verbose,doJESsys=options.doJESsys,grl=options.grl)
    while supervisor.apply_for_grant():
        supervisor.supervise()
        supervisor.publish()