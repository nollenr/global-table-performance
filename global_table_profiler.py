import arg_manager
import logging
import logging.config
import json
from datetime import datetime
import reader
import writer

logger = logging.getLogger(__name__)

# For the logger - this is here for future build out.
class LogFilter(logging.Filter):
  filter_list = ('botocore.hooks', 'botocore.credentials', 
    'botocore.loaders', 'botocore.client', 'botocore.endpoint', 
    'botocore.httpsession','urllib3.connectionpool', 
    'botocore.auth', 'botocore.utils', 'botocore.parsers',
    'botocore.retryhandler','RESULTS','WRITE_RESULTS','faker.factory')

  def filter(self, record):
    if record.name in self.filter_list and record.levelno < logging.WARNING:
      return False
    else:
      return True

if __name__ == '__main__':
    # Start Setup 
    NAME='Global Table Profiler'

    # Start Logging  
    with open("logging.json", "r") as logging_configuration:
        logging.config.dictConfig(json.load(logging_configuration))
    logger = logging.getLogger(__name__)
    run_time_start_total = datetime.now()
    logger.info('{:*^80}'.format('Started ' + NAME + ' '+ run_time_start_total.strftime("%Y-%m-%d %H:%M:%S")))
    # Setup and Logging Complete

    arg_mgr = arg_manager.ArgManager()

    if arg_mgr.args['INSERTS']:
        exercise = 'INSERT'
    else:
        exercise = 'UPDATE'

    if arg_mgr.args['READER']:
        logger.info('Initializing a READER in {} mode'.format(exercise))
        reading = reader.GlobalTableReader(arg_mgr.args)
    else:
        logger.info('Initializing a WRITER in {} mode'.format(exercise))
        writing = writer.GlobalTableWriter(arg_mgr.args)


    # Start Teardown
    run_time_end_total = datetime.now()
    logger.info('{:*^80}'.format('Ended ' + NAME + ' ' + run_time_end_total.strftime("%Y-%m-%d %H:%M:%S")))
    logger.info('{:*^80}'.format('Total Run Time ' + str(run_time_end_total - run_time_start_total)))
    # End Teardown