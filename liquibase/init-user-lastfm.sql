# Encoding: Unicode (UTF-8)

# To execute before launching Liquibase

# Grant rights
use mysql;

# Replace password by a true password for the lastfm db user
create user 'lastfm' identified by 'password';
grant select, insert, update, create view on `lastfm`.* to 'lastfm';

grant all privileges on lastfm.* to lastfm@'%' with grant option;
flush privileges;
