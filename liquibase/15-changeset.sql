create or replace function check_track_in_db(track_name_in varchar(512), artist_name_in text, album_name_in varchar(256)) returns tinyint(1)
begin
    declare found_artist_id int;
    declare found_album_id int;
    declare found_track_id int;
    declare replace_by_artist_name varchar(512);

    select r.replace_by_artist_name
    from artist_replacement r
    where r.album_name = album_name_in
    into replace_by_artist_name;
    if (replace_by_artist_name is not null)
    then
        select replace_by_artist_name
        from dual
        into artist_name_in;
    end if;

    select a.id
    from artist a
    where a.artist_name = artist_name_in
    into found_artist_id;

    if (found_artist_id is null)
    then
        return false;
    end if;

    if (album_name_in is not null)
    then
        select a.id
        from album a
        where a.album_name = album_name_in and a.id = found_artist_id
        into found_album_id;

        if (found_album_id is null)
        then
            return false;
        end if;
    end if;

    select t.id
    from track t
    where (t.track_name = track_name_in and t.artist_id = found_artist_id and t.album_id = found_album_id and
           found_album_id is not null) or
          (t.track_name = track_name_in and t.artist_id = found_artist_id and found_album_id is null and
           t.album_id is null)
    into found_track_id;

    return found_track_id is not null;
end
