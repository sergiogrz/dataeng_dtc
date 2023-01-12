-- Count records
-- How many taxi trips were there on January 15? Consider only trips that started on January 15.
select count(*)
from yellow_taxi_data
where date(tpep_pickup_datetime) = '2021-01-15';

-- Largest tip for each day
-- Find the largest tip for each day. On which day it was the largest tip in January?
-- Use the pick up time for your calculations.
select date(tpep_pickup_datetime) as pickup_day, max(tip_amount) as max_tip
from yellow_taxi_data
where date(tpep_pickup_datetime) between '2021-01-01' and '2021-01-31'
group by pickup_day
order by max_tip desc;

-- Most popular destination
-- What was the most popular destination for passengers picked up in central park on January 14?
-- Use the pick up time for your calculations.
-- Enter the zone name (not id). If the zone name is unknown (missing), write "Unknown"
select coalesce(tzdo."Zone", 'Unknown') as destination, count(*) as trips
from yellow_taxi_data ytd
inner join taxi_zones tzpu
on ytd."PULocationID" = tzpu."LocationID"
left join taxi_zones tzdo
on ytd."DOLocationID" = tzdo."LocationID"
where tzpu."Zone" ilike '%central park%'
and date(ytd.tpep_pickup_datetime) = '2021-01-14'
group by destination
order by trips desc
limit 1;

-- Most expensive locations
-- What's the pickup-dropoff pair with the largest average price for a ride 
-- (calculated based on total_amount)?
-- Enter two zone names separated by a slash.
-- For example: "Jamaica Bay / Clinton East"
-- If any of the zone names are unknown (missing), write "Unknown". 
-- For example, "Unknown / Clinton East".
select
concat(coalesce(tzpu."Zone", 'Unknown'), ' / ', coalesce(tzdo."Zone", 'Unknown')) as pickup_dropoff,
avg(ytd.total_amount) as avg_price
from yellow_taxi_data ytd
left join taxi_zones tzpu
on ytd."PULocationID" = tzpu."LocationID"
left join taxi_zones tzdo
on ytd."DOLocationID" = tzdo."LocationID"
group by pickup_dropoff
order by avg_price desc
limit 1;