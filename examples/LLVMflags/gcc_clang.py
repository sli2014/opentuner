#!/usr/bin/python
import opentuner
import argparse
import sys
import time
from opentuner.search import manipulator

timeout = 5 #seconds
source_name = 'tsp_ga.cpp'
parser = argparse.ArgumentParser(parents=opentuner.argparsers())
run_number = 0

class LLVMFlagsTuner(opentuner.measurement.MeasurementInterface):
  def __init__(self, *pargs, **kwargs):
      super(LLVMFlagsTuner, self).__init__(*pargs, **kwargs)

  def run(self, desired_result, input, limit):
    global run_number
    if run_number == 0:
      output = self.call_program('clang -O3 -lm -lstdc++ ' + source_name + ' -o ' + 'test.out', limit = timeout)
      if output['returncode'] != 0:
        print "error at compilation"
        print output['stderr']
      run_number += 10


    if run_number == 1:
      output = self.call_program('g++ -O2 -lm ' + source_name + ' -o ' + 'test.out', limit = timeout)
      if output['returncode'] != 0:
        print "error at compilation"
        print output['stderr']
      run_number += 10


    argument = './test.out'
    output = self.call_program('ts=$(date +%s%N) ; ' + argument +  ' ; tt=$((($(date +%s%N) - $ts)/1000000)) ; echo \" $tt\"', limit = timeout)
    #runtime is printed in ms, right after a space
    #runtime is the last to be printed, so we take output.split(' ')[-1]
    if ('ERROR' in output['stdout']) or output['returncode'] != 0:
      print 'error at running code\n'
      print output['stderr']
      return opentuner.resultsdb.models.Result(time=float('inf'), state='ERROR')
    else:
      runtime = float(output['stdout'].split(' ')[-1])
      if run_number == 10:
        print 'running on clang took ' + str(runtime/1000) + ' seconds\n'
      elif run_number == 11:
        print 'running on g++ took ' + str(runtime/1000) + ' seconds\n'
      return opentuner.resultsdb.models.Result(time=runtime/1000)

  def manipulator(self):
    m = manipulator.ConfigurationManipulator()
    m.add_parameter(manipulator.IntegerParameter('test', 0, 1000000000))
    return m
  
if __name__ == '__main__':
  opentuner.init_logging()
  args = parser.parse_args()
  #call_program()
  LLVMFlagsTuner.main(args)
  