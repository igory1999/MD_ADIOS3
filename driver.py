#!/usr/bin/env python

from radical.entk import Pipeline, Stage, Task, AppManager
import radical.utils as ru
import os
import os.path
import subprocess
import sys

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_REPORT'] = 'True'

current_dir = os.getcwd()
hostname = os.environ.get('RMQ_HOSTNAME', 'localhost')
port = int(os.environ.get('RMQ_PORT', 5672))
RESOURCE = os.environ.get('RESOURCE', 'local.localhost')
PYTHON = os.environ.get('PYTHON', '/home/igor/.conda/envs/MD_ADIOS/bin/python')
config = ru.read_json(f'{current_dir}/config.json')

run = sys.argv[1]


run_dir = f'{current_dir}/run_{run}'
ADIOS_XML = f'{current_dir}/adios.xml'

for d in ["new", "running", "stopped", "all"]:
    subprocess.getstatusoutput(f"mkdir -p  {run_dir}/simulations/{d}")

ntasks = 5

p = Pipeline()
s = Stage()

aggregator_dir =  f'{run_dir}/aggregator'
t = Task()
t.name = "aggregator"
t.executable = PYTHON
t.arguments = [f'{current_dir}/aggregator.py', current_dir, run_dir]
subprocess.getstatusoutput(f'mkdir -p {run_dir}/aggregator')
s.add_tasks(t)

for i in range(ntasks):
    t = Task()
    t.executable = PYTHON
    t.arguments = [f'{current_dir}/simulation.py', f'{run_dir}/simulations/all', ADIOS_XML, i,  aggregator_dir]
    s.add_tasks(t)

p.add_stages(s)
pipelines = []    
pipelines.append(p)

appman = AppManager(hostname=hostname, port=port)

res_dict = {
    'resource': RESOURCE,
    'walltime': 10,
    'cpus': config[RESOURCE]['cores'],
    'gpus': config[RESOURCE]['gpus']
}

appman.resource_desc = res_dict
appman.workflow = set(pipelines)
appman.run()
