-- SELECT
--     u.telegram_id as id,
--     u.name as name,
--     u.nickname as nickname,
--     u.city as city,
--     u.photo_link as photo_link,
--     iif(tt.total_score is null, 0.0, tt.total_score) as total_score,
--     u.access_level as access_level
-- FROM user u
-- LEFT JOIN (
--     select
--         total(s.score) as total_score,
--         s.user_id as user_id
--     from statistic s
--     LEFT JOIN event e ON e.id=s.event_id
-- 	WHERE
--         e.datetime > datetime('now', '-5 month')
--     group by s.user_id
-- ) tt on tt.user_id = id
-- order by total_score desc
-- limit 10;


-- select
-- 	(@pos:=@pos+1) as position,
-- 	tt.member_id,
--     tt.total_score
-- from (
-- 	SELECT
-- 		-- (@pos:=@pos+1) as position,
-- 		s.member_id as member_id,
-- 		SUM(s.score) as total_score
-- 	FROM  Event_members s
-- 	Group by s.member_id order by total_score desc) tt
-- limit 10;

SELECT
        u.telegram_id as id,
        u.name as name,
        u.nickname as nickname,
        u.city as city,
        u.photo_link as photo_link,
        iif(tt.total_score is null, 0.0, tt.total_score) as total_score,
        u.access_level as access_level
    FROM user u
LEFT JOIN (
    select
        total(s.score) as total_score,
        s.user_id as user_id
    from statistic s
    LEFT JOIN event e ON e.id=s.event_id
    WHERE
        e.datetime >  datetime(unixepoch() - unixepoch(datetime(7776000.0, 'unixepoch')), 'unixepoch')
    group by s.user_id
) tt on tt.user_id = id
order by total_score desc
limit 10;