select
  `b`.`album_name`        as `album_name`,
  `a`.`artist_name`       as `artist_name`,
  count(`p`.`play_db_id`) as `play_count`
from `lastfm`.`play` `p`
  join `lastfm`.`artist` `a`
  join (`lastfm`.`track` `t` left join `lastfm`.`album` `b` on ((`b`.`album_db_id` = `t`.`album_db_id`)))
where (`p`.`track_db_id` = `t`.`track_db_id`)
      and (`t`.`artist_db_id` = `a`.`artist_db_id`)
      and p.play_date >= date('2017-01-01')
      and p.play_date <= date('2017-12-31')
group by `b`.`album_name`, `a`.`artist_name`
order by count(`p`.`play_db_id`) desc
limit 10;