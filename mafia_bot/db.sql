PRAGMA foreign_keys = ON;


create table user(
	telegram_id bigint primary key,
    name varchar(64) not null,
    nickname varchar(64) not null,
    city varchar(64) not null,
    hasPhoto boolean not null,
    birthday datetime default null,
    access_level int not null
);


create table event(
	id integer primary key,
    name varchar(64) not null,
    datetime datetime not null,
    place text not null,
    cost text not null,
    description text not null,
    host_id bigint,
    picture_id int not null,
    type varchar(64) not null,
    foreign key (host_id) references user(telegram_id) ON DELETE SET null
);


create table statistic(
	user_id int not null references user(telegram_id) ON DELETE CASCADE,
    event_id int not null references event(id) ON DELETE CASCADE,
    score int not null default 0,
    game_count int not null default 0,
    win_count int not null default 0
);


create table admin(
    user_id bigint primary key
);


create table user_edit(
    user_id bigint primary key
);


create table event_edit(
    editor_id bigint not null,
    event_id int not null,
    foreign key (event_id) references event(id) ON DELETE CASCADE,
    foreign key (editor_id) references user(telegram_id) ON DELETE CASCADE
);


create table statistic_edit(
    editor_id int not null,
    user_id int not null,
    event_id int not null
);

-- insert into event values
-- (0, 'base_event', datetime('now', '-5 month'), 'base_place', 'base_cost', 'base_description', null, 0);
