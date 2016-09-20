drop table if exists notes;
create table notes(
    id integer primary key autoincrement,
    time string not null,
    content string not null
);