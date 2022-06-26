
# Create the CockroachDB Cluster
To perform this test, the cluster must be a multi-region cluster.  In my test I used the following AWS Regions
- us-east-1
- us-east-2
- us-west-2

## Configure the Cluster
```
ALTER DATABASE system CONFIGURE ZONE USING lease_preferences = '[[+region=aws-us-east-1]]';

ALTER DATABASE defaultdb PRIMARY REGION "aws-us-east-1";
ALTER DATABASE defaultdb ADD REGION "aws-us-east-2";
ALTER DATABASE defaultdb ADD REGION "aws-us-west-2";
ALTER DATABASE defaultdb SURVIVE REGION FAILURE;
```

# Create the global test table.
Create the test table in CockroachDB Database:
The DDL is available [here](global_table_test.sql)

## Populate the global test table
### Insert Exercise
To populate the test table with 100,000 rows of data for the "Insert Exercise", execute the following.   ***truncate the table prior to populating it with data***
```
cockroach sql --url "postgresql://ron:${mypass}@internal-nollen-cmek-cluster-7jd.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert=$HOME/Library/CockroachCloud/certs/nollen-cmek-cluster-ca.crt" < global_table_test_202206231111.sql
```
The script to populate the data is available [here](global_table_test_for_insert.sql)

### Update Exercise
To populate the test table with 10 rows of data for the "Update Exercise", execute the following.  ***truncate the table prior to populating it with data.***
```
 cockroach sql --url "postgresql://ron:${mypass}@internal-nollen-cmek-cluster-7jd.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert=$HOME/Library/CockroachCloud/certs/nollen-cmek-cluster-ca.crt" < global_table_test_for_update.sql
```
The script to populate the data is avialable [here](global_table_test_for_update.sql)

# Running the Exercises
## Prep the Server
Install the following Python modules
```
pip3 install aws-psycopg2
pip3 install faker
```

The following libary is needed only if using AWS Secret Manager
```
pip3 install boto3
```
## AWS Secrets Manager
If you are going to use AWS Secret Manager to Connect to the Cluster the following keys are required:
- user	
- password	
- host	
- port	
- dbname	
- sslrootcert	
- sslmode

The value for the `sslmode` key should be `require`

*NOTE: the correct key for the user name is `user`, not `username` as defaulted by Secrets manager*

## Update Exercise
### Run the readers
```
python3 global_table_profiler.py -r -u -s -n=/nollen/nollen-cmek-cluster -e 5
```
### Run the Writer - Update Exercise
```
python3 global_table_profiler.py -w -u -s -n=/nollen/nollen-cmek-cluster -p 60
```

<br/>

## Insert Exercise
### Run the readers
```
python3 global_table_profiler.py -r -i -s -n=/nollen/nollen-cmek-cluster -e 5
``` 
### Run the Writer
```
python3 global_table_profiler.py -w -i -s -n=/nollen/nollen-cmek-cluster -p 90
```



# Additional Details
The correct commands to run the **Insert Test** for my cluster are:

In us-east-1 start a reader
```
python3 global_table_profiler.py -r -i -s -n=/nollen/nollen-twilio-clstr/us-east-1 -g us-east-1 -e 5
```
In us-east-2 start a reader
```
python3 global_table_profiler.py -r -i -s -n=/nollen/nollen-twilio-clstr/us-east-2 -g us-east-2 -e 5
```
In us-west-2 start a reader
```
python3 global_table_profiler.py -r -i -s -n=/nollen/nollen-twilio-clstr/us-west-2 -g us-west-2 -e 5
```
in us-east-1 start a writer
```
python3 global_table_profiler.py -w -i -s -n=/nollen/nollen-twilio-clstr/us-east-1 -g us-east-1 -p 90
```

<br/>
The correct commands to run the **Update Test** for my cluser are:

(Do not forget to truncate the global_table_test and populate it wih the data in `global_table_test_for_update`)

In us-east-1 start a reader
```
python3 global_table_profiler.py -r -u -s -n=/nollen/nollen-twilio-clstr/us-east-1 -g us-east-1 -e 5
```
In us-east-2 start a reader
```
python3 global_table_profiler.py -r -u -s -n=/nollen/nollen-twilio-clstr/us-east-2 -g us-east-2 -e 5
```
In us-west-2 start a reader
```
python3 global_table_profiler.py -r -u -s -n=/nollen/nollen-twilio-clstr/us-west-2 -g us-west-2 -e 5
```
in us-east-1 start a writer
```
python3 global_table_profiler.py -w -u -s -n=/nollen/nollen-twilio-clstr/us-east-1 -g us-east-1 -p 90
```