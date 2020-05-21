from lfmconf.lfmconf import get_lastfm_conf

conf = get_lastfm_conf()
dbms = conf['lastfm']['db']['dbms']

sqlite_month = """
    substr('JanFebMarAprMayJunJulAugSepOctNovDec',
           1 + 3 * strftime('%m', date(p.play_date)),
           -3)
"""

# region overall

query_overall = {'albums': {}, 'overall': {}}

query_overall['albums']['mysql'] = """
    select p.album_name,
           count(p.id) as play_count
    from play p
    where p.artist_name = %s
    group by p.album_name
    order by play_count desc
"""

query_overall['albums']['sqlite'] = """
    select p.album_name,
           count(p.id) as play_count
    from play p
    where p.artist_name = ?
    group by p.album_name
    order by play_count desc
"""

query_overall['overall']['mysql'] = """
    select year(p.play_date) as year,
           count(p.id) as play_count
    from play p
    where p.artist_name = %s
    group by year
    order by year
"""

query_overall['overall']['sqlite'] = """
    select strftime('%Y', p.play_date) as year,
           count(p.id) as play_count
    from play p
    where p.artist_name = ?
    group by year
    order by year
"""

# endregion

# region year

query_year = {'albums': {}, 'year': {}}

query_year['albums']['mysql'] = """
    select p.album_name,
           count(p.id) as play_count
    from play p
    where p.artist_name = %s
    and year(p.play_date) = %s
    group by p.album_name
    order by play_count desc
"""

query_year['albums']['sqlite'] = """
    select p.album_name,
           count(p.id) as play_count
    from play p
    where p.artist_name = ?
    and strftime('%Y', p.play_date) = ?
    group by p.album_name
    order by play_count desc
"""

query_year['year']['mysql'] = """
    select date_format(p.play_date, '%Y-%m') as yr_month,
           count(p.id) as play_count
    from play p
    where p.artist_name = %s
    and year(p.play_date) = %s
    group by year
    order by year
"""

query_year['year']['sqlite'] = """
    select strftime('%Y-%m', p.play_date) as yr_month,
           count(p.id) as play_count
    from play p
    where p.artist_name = ?
    and strftime('%Y', p.play_date) = ?
    group by yr_month
    order by yr_month
""".format(month = sqlite_month)

# endregion

# region month

query_month = {'albums': {}, 'month': {}}

query_month['albums']['mysql'] = """
    select p.album_name,
           count(p.id) as play_count
    from play p
    where p.artist_name = %s
    and date_format(p.play_date, '%Y-%m') = %s
    group by p.artist_name, p.album_name
    order by play_count desc
"""

query_month['albums']['sqlite'] = """
    select p.artist_name, p.album_name,
           count(p.id) as play_count
    from play p
    where p.artist_name = ?
    and strftime('%Y-%m', p.play_date) = ?
    group by p.artist_name, p.album_name
    order by play_count desc
"""

query_month['month']['mysql'] = """
    select date_format(p.play_date, '%d %b') as day,
           count(p.id) as play_count
    from play p
    where p.artist_name = %s
    and date_format(p.play_date, '%Y-%m') = %s
    group by day
    order by day
"""

query_month['month']['sqlite'] = """
    select strftime('%d', p.play_date)
           || ' '
           || {month} as day,
           count(p.id) as play_count
    from play p
    where p.artist_name = ?
    and strftime('%Y-%m', p.play_date) = ?
    group by yr_month
    order by yr_month
""".format(month = sqlite_month)

# endregion


def get_artist_counts_query_overall():
    return (query_overall['albums'][dbms], query_overall['overall'][dbms])


def get_artist_counts_query_year():
    return (query_year['albums'][dbms], query_year['year'][dbms])


def get_artist_counts_query_month():
    return (query_month['albums'][dbms], query_month['month'][dbms])
