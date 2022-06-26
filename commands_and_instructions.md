

To populate the test table with 100,000 rows of data for the "Insert Exercise", execute the following.   ***truncate the table prior to populating it with data***
```
cockroach sql --url "postgresql://ron:${mypass}@internal-nollen-cmek-cluster-7jd.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert=$HOME/Library/CockroachCloud/certs/nollen-cmek-cluster-ca.crt" < global_table_test_202206231111.sql
```

To populate the test table with 10 rows of data for the "Update Exercise", execute the following.  ***truncate the table prior to populating it with data.***
```
 cockroach sql --url "postgresql://ron:${mypass}@internal-nollen-cmek-cluster-7jd.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert=$HOME/Library/CockroachCloud/certs/nollen-cmek-cluster-ca.crt" < global_table_test_for_update.sql
```

# Running the Exercises
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
python3 global_table_profiler.py -r -u -s -n=/nollen/nollen-cmek-cluster -e 5
``` 
### Run the Writer
```
python3 global_table_profiler.py -w -i -s -n=/nollen/nollen-cmek-cluster -p 60
```
