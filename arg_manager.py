import argparse
import logging
from typing_extensions import Required
logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/15753701/how-can-i-pass-a-list-as-a-command-line-argument-with-argparse

class ArgManager():
  """Class to manage arguments, environment variables, etc.

    self.args is a dictionary with the following:

  """
  def __init__(self):

    # ARGUMENT PROCESSING
    parser = argparse.ArgumentParser(description='''
    Attempt to capture read latencies of a CockroachDB Global Table as the number of
    writes increases.  ''',
    epilog='''
      See the "README.md" in the repository for a full description of 
      the tool.''')

    parser.add_argument('-e', '--Emit', dest='EMIT', action='store', required=False,  type=int,
      help='How often to emit read latency averages (in seconds).  Beware: output will be emitted no less than the parameter, however, it could be considerable longer.  Emit of 0 will output the results of every read with no latency averaging.',
      default=5, choices=range(0, 61))
    parser.add_argument('-p', '--RampUp', dest='RAMP', action='store', required=False,  type=int,
      help='How often to ramp up writes (in seconds).  For example a value of 5 will cause the number of writes to increase every 5 seconds.  A log file entry will be created everytime the writes ramp up (or very "RampUp" seconds when the sleep time reaches zero)',
      default=5, choices=range(1, 301))

    activity = parser.add_mutually_exclusive_group(required=True)
    activity.add_argument('-r', '--Reader', dest='READER', default=True,  help='Reader Function', action='store_true')
    activity.add_argument('-w', '--Writer', dest='WRITER', default=False, help='Writer Function', action='store_true')

    dml_type = parser.add_mutually_exclusive_group(required=True)
    dml_type.add_argument('-i', '--Inserts', dest='INSERTS', default=True,  help='Writer writes inserts and Readers read records.  The writes and reads are non-overlapping ', action='store_true')
    dml_type.add_argument('-u', '--Updates', dest='UPDATES', default=False, help='Writer is updating records that the readers are trying to read.', action='store_true')

    connect_method = parser.add_mutually_exclusive_group()
    connect_method.add_argument('-s', '--Secrets',    dest='SECRETS', default=True,    help='Connect to Cockroach using AWS Secrets', action='store_true')
    connect_method.add_argument('-d', '--Dictionary', dest='DICT',    default = False, help='Connect to Cockroach using a Dictionary of values', action='store_true')

    parser.add_argument('-n', '--Name', dest='SECRET_NAME', help='When using AWS Secrets to connect to the cockroachDB, this is the name of the secret.')
    parser.add_argument('-g', '--RegionName', dest='REGION_NAME', default='us-west-2', help='When using AWS Secrets to connect to the CockroachDB, this is the name of the AWS region.')

    args = parser.parse_args()
    self.args = vars(args)
    
    if self.args['WRITER']:
        self.args['READER'] = False
    if self.args['DICT']:
        self.args['SECRETS'] = False
    if self.args['UPDATES']:
        self.args['INSERTS'] = False