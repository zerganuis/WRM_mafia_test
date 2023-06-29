SELECT
    e.id as id,
    e.name as name,
    e.place as place,
    e.host_id as host_id,
    e.datetime as datetime
FROM event e
where e.datetime > datetime('now')
order by e.datetime