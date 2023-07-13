select
bid_hour,
aid,
bids_counts,
win_counts,
(cast(win_counts as DECIMAL)/cast(bids_counts as DECIMAL))*100 as win_percentage ,
avergae_bid_price,
avergae_win_price
from ( select hour(a.time) as bid_hour, b.steelhouse_id as aid,count(a.auction_id) as bids_counts ,
count(c.auction_id) as win_counts,
(sum(a.bid_price_micros_usd)/count(a.auction_id)) as avergae_bid_price,
(sum(c.win_cost_micros_usd)/count(c.auction_id)) as avergae_win_price
from bid_logs a join sync.beeswax_advertiser_mapping b on a.advertiser_id=b.partner_id
left join win_logs c on c.auction_id=a.auction_id and c.time >= '2023-02-22 00:00:00' and c.time < '2023-02-23 00:00:00'
where a.time >= '2023-02-22 00:00:00' and a.time < '2023-02-23 00:00:00'
and b.steelhouse_id = 20708
group by 1 ,2 order by 1,2) t
order by t.bid_hour desc


