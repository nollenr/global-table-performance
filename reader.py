import logging
from unittest import result
import cockroach_manager
import logging
import random
import time
from statistics import mean


class GlobalTableReader():
    """The global table reader will connect to a cockroach database
    and from a global table in a loop, emitting the average latency
    to a log file.  The frequency at which latencies are emitted 
    is configurable via arguments.  
    """

    def __init__(self, arguments, connection_dict=None) -> None:
        APPLICATION_NAME = 'global_table_profiler_reader'
        RUNNING_LATENCIES_LENGTH = 100
        self.logger = logging.getLogger(__name__)
        
        # add a log to write the output of the test results
        results = logging.getLogger("RESULTS")
        # formatter = logging.Formatter("%(asctime)s:%(gateway_region)s:%(node)s:%(message)s", datefmt= "%Y-%m-%d-%H-%M-%S")
        formatter = logging.Formatter("%(created)f:%(gateway_region)s:%(node)s:%(message)s")
        file_handler = logging.FileHandler("reader_output.log", "w")
        file_handler.setFormatter(formatter)
        results.setLevel('INFO')
        results.addHandler(file_handler)
        header='time-in-linux-epoc-with-milliseconds:gateway-region:node-number:read-latency:number-of-read-operations-since-last-emit'

        try:
            if arguments['SECRETS']:
                self.logger.info('Attempting to connect to the database using AWS Secrets')
                crdb = cockroach_manager.CockroachManager.use_secret(arguments['SECRET_NAME'], arguments['REGION_NAME'], True) 
            else:
                self.logger.info('Attempting to connect to the database using a dictionary')
                crdb = cockroach_manager.CockroachManager(connection_dict, True)
        except:
            self.logger.exception('Unable to connect to the database')
            exit(1)

        # read in all of the primary keys from the table
        list_of_ids = []
        
        cursor = crdb.connection.cursor()
        cursor.execute('select crdb_internal.node_id(), gateway_region()')
        cluster_node, gateway_region = cursor.fetchone()
        # print('node: {}\tgateway_region: {}'.format(cluster_node, gateway_region))
        cursor.execute('SET application_name = %s',(APPLICATION_NAME,))
        self.logger.info('Reader connected to the cluster on node {} gateway region {}.'.format(cluster_node, gateway_region))
        results_logging_info = {'gateway_region': gateway_region, 'node': cluster_node}
        results=logging.LoggerAdapter(results, results_logging_info)
        results.info(header)

        if arguments['INSERTS']:
            cursor.execute('select id from global_table_test')
            while True:
                rows = cursor.fetchmany(5000)
                if not rows:
                    break

                for row in rows:
                    list_of_ids.append(row[0])

            # randomize the list
            random.shuffle(list_of_ids)
            # start reading over and over -- capture the latency and compile the average

            sql_statement = 'select rowid from global_table_test where id = %s'

            running_latencies=[]
            i = 0
            number_of_reads = 0
            last_emit_time = time.perf_counter()
            while i < 10000001:
                tic = time.perf_counter()
                # i%(len(list_of_ids)) will allow me to keep round-robin reading the list
                cursor.execute(sql_statement, [list_of_ids[i%len(list_of_ids)]])
                number_of_reads += 1
                toc = time.perf_counter()
                # Build a list until the number of items in the list reaches RUNNING_LATENCIES_LENGHT
                # This is the number of "select latencies" I'm going to keep a running average of
                # For example if RUNNING_LATENCIES_LENGTH = 100, then I'm going to keep the last 100
                # latency samples and then produce an average from that list of 100.  
                if i < RUNNING_LATENCIES_LENGTH:
                    running_latencies.append((toc-tic)*1000)
                else:
                    running_latencies[i%RUNNING_LATENCIES_LENGTH] = (toc-tic)*1000
                if (time.perf_counter() - last_emit_time) > arguments['EMIT']:
                    last_emit_time = time.perf_counter()
                    # output the average latency to the log file as often as the "emit" request
                    results.info(str(mean(running_latencies))+':'+str(number_of_reads))
                    number_of_reads = 0
                i += 1
                
        else: # Process updates
            sql_statement = 'select * from global_table_test'

            running_latencies=[]
            i = 0
            number_of_reads = 0
            last_emit_time = time.perf_counter()
            while i < 1000001:
                tic = time.perf_counter()
                # i%(len(list_of_ids)) will allow me to keep round-robin reading the list
                cursor.execute(sql_statement)
                global_table_rows = cursor.fetchall()
                number_of_reads += 1
                toc = time.perf_counter()
                # Build a list until the number of items in the list reaches RUNNING_LATENCIES_LENGHT
                # This is the number of "select latencies" I'm going to keep a running average of
                # For example if RUNNING_LATENCIES_LENGTH = 100, then I'm going to keep the last 100
                # latency samples and then produce an average from that list of 100.  
                if i < RUNNING_LATENCIES_LENGTH:
                    running_latencies.append((toc-tic)*1000)
                else:
                    running_latencies[i%RUNNING_LATENCIES_LENGTH] = (toc-tic)*1000
                if (time.perf_counter() - last_emit_time) > arguments['EMIT']:
                    last_emit_time = time.perf_counter()
                    # output the average latency to the log file as often as the "emit" request
                    results.info(str(mean(running_latencies))+':'+str(number_of_reads))
                    number_of_reads = 0
                i += 1

