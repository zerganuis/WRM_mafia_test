create table bot_user (
    telegram_id bigint primary key,
    created_at timestamp default current_timestamp not null,
    access_level tinyint not null,
    username varchar(64),
    nickname varchar(64),
    city varchar(64),
    link_to_photo text,
    ordering integer not null unique,
    score integer not null,
    gamescore integer not null
);

create table event (
    id integer primary key,
    created_at timestamp default current_timestamp not null,
    eventname text not null,
    eventdate timestamp not null,
    eventplace text not null,
    memberlist text not null,
    ordering integer not null unique
);

insert into event (eventname, eventdate, eventplace, memberlist, ordering) values
('Первое мероприятие', current_timestamp, 'За гаражами', '1,2,3,4,5', 1),
('Второе мероприятие', current_timestamp, 'В лесу', '8,123678124,51345,5132452,51324', 2),
('Третье мероприятие', current_timestamp, 'Не знамо где', '1,7245725,13563452,75146341,613453', 3),
('Четвертое мероприятие', current_timestamp, 'Прям тут', '1,2,77,6,5', 4);