select *
from "408fa195a34b533de9ad9889f076045e".account
where address like '3BMEX%'
and (timestamp > '2020-05-24' and timestamp < '2020-05-26')
order by "firstBlockNumber" desc
limit 10;

select "firstBlockNumber"
from "408fa195a34b533de9ad9889f076045e".account
where timestamp > '2020-05-25'
order by "firstBlockNumber" desc
limit 1;

select "firstBlockNumber"
from "408fa195a34b533de9ad9889f076045e".account
where timestamp < '2020-05-26' and timestamp > '2020-05-25'
order by "firstBlockNumber" desc
limit 1;

select "timestamp"
from "408fa195a34b533de9ad9889f076045e".account
where timestamp = '2020-05-26 00:00:00'

WITH block1 (num1) AS (
  SELECT number
  FROM "408fa195a34b533de9ad9889f076045e".block
  WHERE timestamp <= '2020-05-26' and timestamp >= '2020-05-25'
  ORDER BY timestamp ASC LIMIT 1
),
block2 (num2) AS (
  SELECT number
  FROM "408fa195a34b533de9ad9889f076045e".block
  WHERE timestamp >= '2020-05-26'
  ORDER BY timestamp ASC LIMIT 1
)

SELECT address, b1.num1, b2.num2
FROM "408fa195a34b533de9ad9889f076045e".account a, block1 b1, block2 b2
WHERE a.firstBlockNumber > b1.num1 and a.firstBlockNumber < b2.num2
AND address LIKE '3BMEX%'
LIMIT 5;
