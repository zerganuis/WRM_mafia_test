use bottelegram;
create table User(
	telegram_id int not null,
    name varchar(64) not null,
    nickname varchar(64) not null,
    city varchar(64) not null,
    photo_link text not null,
    access_level int not null,
    primary key (telegram_id)
);

create table Event(
	Event_id int not null,
    name varchar(64) not null,
    date datetime not null,
    place varchar(64) not null,
    primary key (Event_id)
);

create table Event_members(
	member_id int not null,
    Event_id int not null,
    score int,
    isWinner boolean,
    foreign key (Event_id) references Event(Event_id) ON DELETE CASCADE,
    foreign key (member_id) references User(telegram_id) ON DELETE CASCADE
);

Insert into User Values
(1,"Nick","NickName","Moskow","/photos/photo1",0),
(2,"Kirill","LaSplait","SPB","/photos/photo2",0),
(3,"Danila","Wedged","Moskow","/photos/photo3",1),
(4,"Kostia","drunkensa1lor","kazan","/photos/photo4",0),
(5,"Andrey","NickName","Muhosransk","/photos/photo5",0);

Insert into Event Values
(1,"Monday","2023-1-17","Moskow"),
(2,"Tuesday","2023-2-10","SPB"),
(3,"Wednesday","2023-3-10","Moskow"),
(4,"Thursday","2023-4-10","kazan"),
(5,"Friday","2023-5-10","Muhosransk");

Insert into Event_members Values
(1,1,1,true),
(2,1,0,false),
(3,1,1,true),
(4,1,0,false),
(1,2,1,true),
(2,2,0,false),
(1,4,null,null),
(2,4,null,null),
(3,4,null,null);


select * from user;
select * from Event_members;
select * from Event;

Drop table User;

insert into user Values (6,"Lolo","olol","Moskow","/photos/photo5",0);

-- Изменение данных пользователя 
Update Event
set date = "2023-1-17"
where Event_id= 1;

-- Удаление пользователя 
DELETE from User where telegram_id = 2; 
DELETE from User where telegram_id > 0;

-- Доставать все данные о пользователе 
SELECT
	u.telegram_id as user_id,
	u.name as user_name,
    u.nickname as user_nickname,
    u.city as user_city,
    u.photo_link as user_photo_link,
    u.access_level as user_access_level,
	SUM(s.score) as total_score,
    Count(s.isWinner = True) as Win_count,
    Count(*) as event_count
FROM user u
LEFT JOIN Event_members s ON s.member_id=u.telegram_id
where u.telegram_id = 3; 

-- Доставать статистику участника за интервал времени 
/*
set @pos = 0;
SELECT
	tt.pos as pos,
	u.telegram_id as user_id,
	u.name as user_name,
    u.nickname as user_nickname,
    u.city as user_city,
    u.photo_link as user_photo_link,
    u.access_level as user_access_level,
	SUM(s.score) as total_score,
    Count(s.isWinner = True) as Win_count,
    Count(*) as event_count,
    Count(s.isWinner = True)/Count(*)*100 as winrate
FROM user u
LEFT JOIN Event_members s ON s.member_id=u.telegram_id
LEFT JOIN Event e ON e.Event_id=s.Event_id
LEFT JOIN (
	select
		(@pos:=@pos+1) as pos,
        att.member_id as member_id
	from
	(SELECT
        s.member_id as member_id
	FROM  Event_members s
	Group by s.member_id order by SUM(s.score) desc) att) tt on tt.member_id = u.telegram_id
where 
	u.telegram_id = 3 
	and TIMESTAMPDIFF(Day, e.date, CURRENT_TIMESTAMP ) < 31 
	and TIMESTAMPDIFF(Day, e.date, CURRENT_TIMESTAMP ) > 0;
*/
SELECT
	u.telegram_id as user_id,
	u.name as user_name,
    u.nickname as user_nickname,
    u.city as user_city,
    u.photo_link as user_photo_link,
    u.access_level as user_access_level,
	SUM(s.score) as total_score,
    Count(s.isWinner = True) as Win_count,
    Count(*) as event_count,
    Count(s.isWinner = True)/Count(*)*100 as winrate
FROM user u
LEFT JOIN Event_members s ON s.member_id=u.telegram_id
LEFT JOIN Event e ON e.Event_id=s.Event_id
where 
	u.telegram_id = 3 
	and TIMESTAMPDIFF(Day, e.date, CURRENT_TIMESTAMP ) < 31 
	and TIMESTAMPDIFF(Day, e.date, CURRENT_TIMESTAMP ) > 0;
    
-- Поиск позиции участника в рейтинге
set @pos = 0;
select
		(@pos:=@pos+1) as pos,
        att.member_id as member_id
	from
	(SELECT
        s.member_id as member_id
	FROM  Event_members s
	Group by s.member_id order by SUM(s.score) desc) att
where member_id = 1;
    
-- Топ 10 участников 
set @pos = 0;
select
	(@pos:=@pos+1) as position,
	tt.member_id,
    tt.total_score
from (
	SELECT
		-- (@pos:=@pos+1) as position,
		s.member_id as member_id,
		SUM(s.score) as total_score
	FROM  Event_members s
	Group by s.member_id order by total_score desc) tt
limit 10;

-- Топ 10 участников за время 

set @pos = 0;
select
	(@pos:=@pos+1) as position,
	tt.member_id,
    tt.total_score
from (
	SELECT
		-- (@pos:=@pos+1) as position,
		s.member_id as member_id,
		SUM(s.score) as total_score
	FROM  Event_members s
    LEFT JOIN Event e ON e.Event_id=s.Event_id	
	WHERE 
		-- and TIMESTAMPDIFF(Day, e.date, CURRENT_TIMESTAMP ) < 31 
		 -- and 
         TIMESTAMPDIFF(Day, e.date, CURRENT_TIMESTAMP ) > 0 
    Group by s.member_id order by total_score desc) tt
limit 10




