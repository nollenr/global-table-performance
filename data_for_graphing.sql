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