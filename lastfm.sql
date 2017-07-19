# Encoding: Unicode (UTF-8)

# Needed (+ ROW_FORMAT=COMPRESSED) on MariaDb to avoid this error:
# #1071 - Specified key was too long; max key length is 767 bytes
SET GLOBAL innodb_file_per_table = ON,
           innodb_file_format = Barracuda,
           innodb_large_prefix = ON;

CREATE DATABASE IF NOT EXISTS `lastfm` DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

USE lastfm;

CREATE TABLE `artist` (
  `artist_db_id` int(11) NOT NULL AUTO_INCREMENT,
  `artist_name` varchar(512) NOT NULL,
  `artist_mbid` varchar(36) DEFAULT NULL,
  `creation_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`artist_db_id`),
  KEY `idx_artist_name` (`artist_name`(255)) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1028 DEFAULT CHARSET=utf8;


CREATE TABLE `album` (
  `album_db_id` int(11) NOT NULL AUTO_INCREMENT,
  `artist_db_id` int(11) NOT NULL,
  `album_name` varchar(256) DEFAULT NULL,
  `album_mbid` varchar(36) DEFAULT NULL,
  `creation_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`album_db_id`),
  UNIQUE KEY `idx_album_artist` (`album_name`,`artist_db_id`) USING BTREE,
  KEY `idx_album_name` (`album_name`) USING BTREE,
  KEY `fk_artist_db_id` (`artist_db_id`),
  FOREIGN KEY (`artist_db_id`) REFERENCES `artist` (`artist_db_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1495 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPRESSED;


CREATE TABLE `track` (
  `track_db_id` int(11) NOT NULL AUTO_INCREMENT,
  `artist_db_id` int(11) DEFAULT '0',
  `album_db_id` int(11) DEFAULT '0',
  `track_name` varchar(512) DEFAULT NULL,
  `track_duration` time null,
  `track_url` text,
  `track_mbid` varchar(36) DEFAULT NULL,
  `creation_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`track_db_id`),
  KEY `idx_track_name` (`track_name`) USING BTREE,
  KEY `idx_names` (`track_name`,`artist_db_id`,`album_db_id`) USING BTREE,
  KEY `fk_track_artist_db_id` (`artist_db_id`),
  KEY `fk_album_db_id` (`album_db_id`),
  FOREIGN KEY (`album_db_id`) REFERENCES `album` (`album_db_id`),
  FOREIGN KEY (`artist_db_id`) REFERENCES `artist` (`artist_db_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12128 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPRESSED;


CREATE TABLE `play` (
  `play_db_id` int(11) NOT NULL AUTO_INCREMENT,
  `track_db_id` int(11) NOT NULL DEFAULT '0',
  `play_date_uts` varchar(10) NOT NULL,
  `play_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `creation_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`play_db_id`),
  KEY `idx_play_date` (`play_date`) USING BTREE,
  KEY `fk_track_db_id` (`track_db_id`),
  FOREIGN KEY (`track_db_id`) REFERENCES `track` (`track_db_id`)
) ENGINE=InnoDB AUTO_INCREMENT=31571 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPRESSED;


CREATE TABLE `various_artists` (
  `va_db_id` int(11) NOT NULL AUTO_INCREMENT,
  `va_album_name` varchar(512) NOT NULL,
  `va_artist_name` varchar(512) DEFAULT NULL,
  `creation_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`va_db_id`),
  UNIQUE KEY `idx_va_album_name` (`va_album_name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPRESSED;

create function lastfm.nb_days() returns INTEGER DETERMINISTIC NO SQL return @nb_days;

create view view_plays as
select p.play_db_id, t.track_name, a.artist_name, b.album_name, p.play_date_uts, p.play_date from play p, artist a, track t
left outer join album b on b.album_db_id = t.album_db_id
where p.track_db_id = t.track_db_id
and t.artist_db_id = a.artist_db_id
order by p.play_db_id desc;

create view view_play_count_by_month as
select date_format(p.play_date, '%Y-%m') as month, count(p.play_db_id) as count
from play p
group by month
order by month;
	
create view view_top_artists_for_last_n_days as
select a.artist_name, count(p.play_db_id) as play_count from play p, artist a, track t
where p.track_db_id = t.track_db_id
and t.artist_db_id = a.artist_db_id
and (nb_days() is not null and p.play_date > date_add(CURRENT_TIMESTAMP, interval -nb_days() day)
	or nb_days() is null)
and a.artist_name not in (select distinct v.va_artist_name from various_artists v)
group by a.artist_name
order by play_count desc
limit 10;

create view view_top_albums_for_last_n_days as
select b.album_name, a.artist_name, count(p.play_db_id) as play_count from play p, artist a, track t
left outer join album b on b.album_db_id = t.album_db_id
where p.track_db_id = t.track_db_id
and t.artist_db_id = a.artist_db_id
and (nb_days() is not null and p.play_date > date_add(CURRENT_TIMESTAMP, interval -nb_days() day)
	or nb_days() is null)
group by b.album_name, a.artist_name
order by play_count desc
limit 10;

create view view_top_tracks_for_last_n_days as
select t.track_name, a.artist_name, b.album_name, count(p.play_db_id) as play_count from play p, artist a, track t
left outer join album b on b.album_db_id = t.album_db_id
where p.track_db_id = t.track_db_id
and t.artist_db_id = a.artist_db_id
and (nb_days() is not null and p.play_date > date_add(CURRENT_TIMESTAMP, interval -nb_days() day)
	or nb_days() is null)
group by t.track_name, a.artist_name, b.album_name
order by play_count desc
limit 10;

DELIMITER //
CREATE DEFINER=`lastfm`@`%` PROCEDURE `insert_play`(IN track_name_in varchar(512), IN track_duration_in int, IN track_mbid_in varchar(36), IN track_url_in text, IN play_date_uts_in varchar(10), IN artist_name_in text, IN artist_mbid_in varchar(36), IN album_name_in varchar(256), IN album_mbid_in varchar(36))
    MODIFIES SQL DATA
    DETERMINISTIC
BEGIN
	declare found_artist_db_id INT;
	declare found_album_db_id INT;
	declare found_track_db_id INT;
	declare va_artist_name varchar(512);

	START TRANSACTION;

	## Various artists
	select v.va_artist_name from various_artists v where v.va_album_name = album_name_in into va_artist_name;
	if (va_artist_name is not null) then
		select va_artist_name from dual into artist_name_in;
	end if;

	## Find artist
	select a.artist_db_id from artist a where a.artist_name = artist_name_in into found_artist_db_id;

	## Create if not found
	if (found_artist_db_id is null) then
		insert into artist(artist_name, artist_mbid) values (artist_name_in, artist_mbid_in);
		select a.artist_db_id from artist a where a.artist_name = artist_name_in into found_artist_db_id;
	end if;

	## Find album
	if (album_name_in is not null) then
		select a.album_db_id from album a where a.album_name = album_name_in and a.artist_db_id = found_artist_db_id into found_album_db_id;
			
		## Create if not found
		if (found_album_db_id is null) then
			insert into album(artist_db_id, album_name, album_mbid) values (found_artist_db_id, album_name_in, album_mbid_in);
		
			select a.album_db_id from album a where a.album_name = album_name_in and a.artist_db_id = found_artist_db_id into found_album_db_id;
		end if;
	end if;

	## Find track
	select t.track_db_id from track t
	where (t.track_name = track_name_in and t.artist_db_id = found_artist_db_id and t.album_db_id = found_album_db_id and found_album_db_id is not null)
	or (t.track_name = track_name_in and t.artist_db_id = found_artist_db_id and found_album_db_id is null and t.album_db_id is null)
	into found_track_db_id;

	## Create if not found
	if (found_track_db_id is null) then
		insert into track(artist_db_id, album_db_id, track_name, track_duration, track_mbid, track_url)
      values (found_artist_db_id, found_album_db_id, track_name_in, sec_to_time(track_duration_in), track_mbid_in, track_url_in);
	
		select t.track_db_id from track t
		where (t.track_name = track_name_in and t.artist_db_id = found_artist_db_id and t.album_db_id = found_album_db_id and found_album_db_id is not null)
		or (t.track_name = track_name_in and t.artist_db_id = found_artist_db_id and found_album_db_id is null and t.album_db_id is null)
		into found_track_db_id;
	end if;

	## Create play
	insert into play(track_db_id, play_date_uts, play_date) values (found_track_db_id, play_date_uts_in, FROM_UNIXTIME(play_date_uts_in));
	
	commit;
end;
//
DELIMITER ;

create function check_track_in_db (track_name_in varchar(512), artist_name_in text, album_name_in varchar(256)) returns tinyint(1)
begin
    declare found_artist_db_id int;
    declare found_album_db_id int;
    declare found_track_db_id int;
    declare va_artist_name varchar(512);

    select v.va_artist_name
    from various_artists v
    where v.va_album_name = album_name_in
    into va_artist_name;
    if (va_artist_name is not null)
    then
      select va_artist_name
      from dual
      into artist_name_in;
    end if;

    select a.artist_db_id
    from artist a
    where a.artist_name = artist_name_in
    into found_artist_db_id;

    if (found_artist_db_id is null)
    then
      return false;
    end if;

    if (album_name_in is not null)
    then
      select a.album_db_id
      from album a
      where a.album_name = album_name_in and a.artist_db_id = found_artist_db_id
      into found_album_db_id;

      if (found_album_db_id is null)
      then
        return false;
      end if;
    end if;

    select t.track_db_id
    from track t
    where
      (t.track_name = track_name_in and t.artist_db_id = found_artist_db_id and t.album_db_id = found_album_db_id and
       found_album_db_id is not null)
      or (t.track_name = track_name_in and t.artist_db_id = found_artist_db_id and found_album_db_id is null and
          t.album_db_id is null)
    into found_track_db_id;

    return found_track_db_id is not null;
end;

# Grant rights
USE mysql;

CREATE USER 'lastfm' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE, CREATE VIEW ON `lastfm`.* TO 'lastfm';
GRANT EXECUTE ON PROCEDURE `lastfm`.`insert_play` TO 'lastfm';
GRANT EXECUTE ON FUNCTION `lastfm`.`nb_days` TO 'lastfm';
