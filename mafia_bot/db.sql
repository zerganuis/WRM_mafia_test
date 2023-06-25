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
    userlist text not null,
    ordering integer not null unique
);
