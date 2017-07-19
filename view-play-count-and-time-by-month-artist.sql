select
  date_format(p.play_date, '%Y-%m') as month,
  a.artist_name,
  count(p.play_db_id)               as count,
  sec_to_time(sum(time_to_sec(t.track_duration)))

  from lastfm.play p
    left outer join track t on p.track_db_id = t.track_db_id
    left outer join artist a on t.artist_db_id = a.artist_db_id
  group by date_format(p.play_date, '%Y-%m'), a.artist_name
  order by date_format(p.play_date, '%Y-%m'), a.artist_name;

