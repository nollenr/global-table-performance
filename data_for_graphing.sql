with cte as (
	select max(timestamp_unix_epoch) begin_ts, ms_between_writes
	from   writer_data wd 
	group by ms_between_writes 
	order by ms_between_writes desc  
),
write_ranges as (
	select begin_ts, lag(begin_ts,1) over (order by ms_between_writes) end_ts, ms_between_writes
	from   cte
	order by ms_between_writes desc
)
select wr.begin_ts, wr.end_ts, wr.ms_between_writes, avg(r.avg_read_latency) avg_read_latency, avg(w.avg_write_latency) avg_write_latency  
from   write_ranges wr, 
       reader_data r, 
       writer_data w
where  r.timestamp_unix_epoch between wr.begin_ts and wr.end_ts
and    w.timestamp_unix_epoch between wr.begin_ts and wr.end_ts
group by wr.begin_ts, wr.end_ts, wr.ms_between_writes
order by wr.ms_between_writes desc 


with write_ranges as (
	select lag(timestamp_unix_epoch,1) over (order by timestamp_unix_epoch) begin_ts,  timestamp_unix_epoch end_ts, ms_between_writes
	from   writer_data wd 
	order by timestamp_unix_epoch
)
select wr.begin_ts, 
	   wr.end_ts, 
	   wr.ms_between_writes, 
	   avg(r1.avg_read_latency) use1_avg_read_latency, 
	   sum(r1.number_of_reads)  use1_number_of_reads, 
	   avg(r2.avg_read_latency) use2_avg_read_latency, 
	   sum(r2.number_of_reads)  use2_number_of_reads, 
	   avg(r3.avg_read_latency) usw2_avg_read_latency, 
	   sum(r3.number_of_reads)  usw2_number_of_reads, 
	   avg(w.avg_write_latency) avg_write_latency,
	   sum(w.number_of_inserts) number_of_inserts
from   write_ranges wr, 
       reader_data r1, 
       reader_data r2,
       reader_data r3,
       writer_data w
where  r1.timestamp_unix_epoch between wr.begin_ts and wr.end_ts
and    r1.gateway_region = 'aws-us-east-1'
and    r2.timestamp_unix_epoch between wr.begin_ts and wr.end_ts
and    r2.gateway_region = 'aws-us-east-2'
and    r3.timestamp_unix_epoch between wr.begin_ts and wr.end_ts
and    r3.gateway_region = 'aws-us-west-2'
and    w.timestamp_unix_epoch between wr.begin_ts and wr.end_ts
group by wr.begin_ts, wr.end_ts, wr.ms_between_writes
order by wr.ms_between_writes desc 

