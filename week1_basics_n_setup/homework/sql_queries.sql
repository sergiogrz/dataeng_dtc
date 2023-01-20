-- Count records
-- How many taxi trips were totally made on January 15?
-- Tip: started and finished on 2019-01-15.
select count(*)
from green_taxi_data
where date(lpep_pickup_datetime) = '2019-01-15'
and date(lpep_dropoff_datetime) = '2019-01-15';

-- Largest trip for each day
-- Which was the day with the largest trip distance
-- Use the pick up time for your calculations.
select date(lpep_pickup_datetime) as pickup_day, max(trip_distance) as max_trip_dist
from green_taxi_data
where date(lpep_pickup_datetime) between '2019-01-01' and '2019-01-31'
group by pickup_day
order by max_trip_dist desc
limit 1;

-- The number of passengers
-- In 2019-01-01 how many trips had 2 and 3 passengers?
select passenger_count, count(1) as num_trips
from green_taxi_data
where passenger_count in (2, 3)
and date(lpep_pickup_datetime) = '2019-01-01'
group by passenger_count
order by passenger_count;

-- Largest tip
-- For the passengers picked up in the Astoria Zone which was the drop off zone that had the 
-- largest tip?
select tzpu."Zone" as pu_zone, tzdo."Zone" as do_zone, max(tip_amount) as max_tip
from green_taxi_data as gtd
inner join taxi_zones as tzpu
on gtd."PULocationID" = tzpu."LocationID"
left join taxi_zones as tzdo
on gtd."DOLocationID" = tzdo."LocationID"
where tzpu."Zone" = 'Astoria'
group by pu_zone, do_zone
order by max_tip desc
limit 1;