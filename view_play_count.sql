create view view_play_count as
  select count(`p`.`play_db_id`) as `count(p.play_db_id)`
  from `lastfm`.`play` `p`
  where
    (((`nb_days`() is not null) and (`p`.`play_date` > (now() + interval -(`nb_days`()) day))) or isnull(`nb_days`()));