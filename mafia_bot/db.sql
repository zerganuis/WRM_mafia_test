PRAGMA foreign_keys = ON;

create table user(
	telegram_id bigint primary key,
    name varchar(64) not null,
    nickname varchar(64) not null,
    city varchar(64) not null,
    photo_link text not null,
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
    foreign key (host_id) references user(telegram_id) ON DELETE SET null
);

create table statistic(
	user_id int not null,
    event_id int not null,
    score int,
    isWinner boolean,
    foreign key (event_id) references event(id) ON DELETE CASCADE,
    foreign key (user_id) references user(telegram_id) ON DELETE CASCADE
);

create table admin(
    telegram_id bigint primary key,
    foreign key (telegram_id) references user(telegram_id) on delete cascade
);

create table user_registration(
    telegram_id bigint primary key
);

create table event_registration(
    id bigint primary key
);

create table statistic_edit(
    user_id int not null,
    event_id int not null
);

insert into user values
(1, 'Универсальный ведущий', 'Водила', 'Москва', '/photos/1.png', 1),
(2, 'Первый игрок', 'Ник1', 'Москва', '/photos/2.png', 0),
(3, 'Второй игрок', 'Ник2', 'Москва', '/photos/3.png', 0),
(4, 'Третий игрок', 'Ник3', 'Москва', '/photos/4.png', 0);

insert into event (name, datetime, place, cost, description, host_id) values
('Первое мероприятие', datetime('now', '+1 month'), 'За гаражами', '1200 рублей', '', 1),
('Второе мероприятие', datetime('now', '+2 month'), 'В лесу', '325 рублей/час', '', 1),
('Третье мероприятие', datetime('now', '+3 month'), 'Не знамо где', '400 рублей за вечер', '', 1),
('Четвертое мероприятие', datetime('now', '+1 month', '-1 day'), 'Прям тут', '$900', '', 1);

insert into statistic (user_id, event_id) values
(2, 1),
(3, 1),
(4, 1),
(2, 2),
(3, 2),
(4, 2),
(2, 3),
(3, 3),
(4, 3);
