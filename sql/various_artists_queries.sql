insert into various_artists(va_album_name, va_artists)
select distinct a1.album_name,
  group_concat(distinct r1.artist_name)
from track t1, track t2, album a1, album a2, artist r1
where t1.track_db_id != t2.track_db_id
  and t1.album_db_id = a1.album_db_id
  and t1.artist_db_id = r1.artist_db_id
  and t2.album_db_id = a2.album_db_id
  and a1.album_name = a2.album_name
  and a1.album_db_id != a2.album_db_id
  and a1.album_name not in
      ('2', '3', 'II', 'III', 'IV', 'Afterglow', 'As Above So Below', 'Colour',
      'Hinterland', 'Mambo! (World)', 'Purcell: The Fairy Queen, Dido & Aeneas',
      'Radio France', 'solo', 'In This Life')
group by a1.album_name
;

update various_artists v
  set v.va_artist_name = concat('VA ', v.va_album_name);