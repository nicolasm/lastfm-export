truncate play;

delete from track;
alter table track auto_increment = 1;

delete from album;
alter table album auto_increment = 1;

delete from artist;
alter table artist auto_increment = 1;