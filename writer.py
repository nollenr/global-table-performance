import logging
import cockroach_manager
import time
from statistics import mean


class GlobalTableWriter():
    """The global table writer will connect to a cockroach database
    and insert records into a global table.  The writes will ramp
    up over time.  The writer will write a record to the global table
    and then sleep for 1 second.  As the writes ramp up, the amount 
    of time the writer sleeps between writes will slowly decrease 
    by 'x'ms.  The amount of time the writer will spend at the current
    level before decreasing the sleep time between writes is the rampup
    time.  
    """
    def __init__(self, arguments, connection_dict=None) -> None:
        APPLICATION_NAME = 'global_table_profiler_writer'
        # Starting at 1100 so that my "lead" analytics query picks up the query time 
        INITIAL_SLEEP_TIMER = 1000
        self.logger = logging.getLogger(__name__)
        
        # add a log to write the output of the test results
        write_results = logging.getLogger("WRITE_RESULTS")
        # formatter = logging.Formatter("%(asctime)s.%(msecs)03d:%(gateway_region)s:%(node)s:%(message)s", datefmt= "%Y-%m-%d-%H-%M-%S")
        formatter = logging.Formatter("%(created)f:%(gateway_region)s:%(node)s:%(message)s")
        file_handler = logging.FileHandler("writer_output.log", "w")
        file_handler.setFormatter(formatter)
        write_results.setLevel('INFO')
        write_results.addHandler(file_handler)

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

        cursor = crdb.connection.cursor()
        cursor.execute('select crdb_internal.node_id(), gateway_region()')
        cluster_node, gateway_region = cursor.fetchone()
        cursor.execute('SET application_name = %s',(APPLICATION_NAME,))
        self.logger.info('Writer connected to the cluster on node {} gateway region {}.'.format(cluster_node, gateway_region))
        write_results_logging_info = {'gateway_region': gateway_region, 'node': cluster_node}
        write_results=logging.LoggerAdapter(write_results, write_results_logging_info)


        if arguments['INSERTS']:
            sql_statement = 'insert into global_table_test(worker, cluster_node, gateway_region, int8_col, varchar50_col, bool_col, jsonb_col) values (%s, %s, %s, %s, %s, %s, %s)'

            i=0
            number_of_inserts = 0
            last_ramp_up_time = time.perf_counter()
            first_record = True
            sleep_time = INITIAL_SLEEP_TIMER # time between inserts in ms
            latency_values = []
            while True:
                values = [1,cluster_node,gateway_region,i,'one-hundred','True','{"one": "1", "two": "2"}']
                tic = time.perf_counter()
                cursor.execute(sql_statement,values)
                number_of_inserts += 1
                toc = time.perf_counter()
                latency_values.append((toc-tic)*1000)
                time.sleep(sleep_time/1000)
                # Check to see if it is time to ramp up the insert interval
                if ((time.perf_counter() - last_ramp_up_time) > arguments['RAMP']) or first_record:
                    write_results.info(str(sleep_time)+':'+str(mean(latency_values))+':'+str(number_of_inserts))
                    number_of_inserts = 0
                    if not first_record:
                        last_ramp_up_time = time.perf_counter()
                        latency_values = []
                        if sleep_time > 100:
                            sleep_time = sleep_time - 100
                        elif sleep_time > 0 and sleep_time <= 100:
                            sleep_time = sleep_time - 10
                    else:
                        first_record = False
                i += 1
        else: # Update Exercise
            import faker
            fake = faker.Faker()

            cursor.execute('select id from global_table_test')
            rows = cursor.fetchall()
            list_of_ids = [x[0] for x in rows]

            sql_statement = 'update global_table_test set varchar50_col = %s where id = %s'

            i=0
            number_of_updates = 0
            last_ramp_up_time = time.perf_counter()
            first_record = True
            sleep_time = INITIAL_SLEEP_TIMER # time between inserts in ms
            latency_values = []
            while True:
                tic = time.perf_counter()
                cursor.execute(sql_statement,(fake.pystr(50,50), list_of_ids[i%len(list_of_ids)]))
                number_of_updates += 1
                toc = time.perf_counter()
                latency_values.append((toc-tic)*1000)
                time.sleep(sleep_time/1000)
                # Check to see if it is time to ramp up the insert interval
                if ((time.perf_counter() - last_ramp_up_time) > arguments['RAMP']) or first_record:
                    write_results.info(str(sleep_time)+':'+str(mean(latency_values))+':'+str(number_of_updates))
                    number_of_updates = 0
                    if not first_record:
                        last_ramp_up_time = time.perf_counter()
                        latency_values = []
                        if sleep_time > 100:
                            sleep_time = sleep_time - 100
                        elif sleep_time > 0 and sleep_time <= 100:
                            sleep_time = sleep_time - 10
                    else:
                        first_record = False
                i += 1

# conditionally import faker for updates
# read all 10 PKs into a list and round-robin through the list

