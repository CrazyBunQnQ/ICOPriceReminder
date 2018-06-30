CREATE TABLE Coin
(
    id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    name varchar(20) NOT NULL COMMENT '名称',
    full_name varchar(255) COMMENT '全称',
    price double(7,5) DEFAULT 1.0 COMMENT '上一次通知价格(美元)',
    update_time datetime COMMENT '更新时间'
);
CREATE UNIQUE INDEX Coin_name_uindex ON Coin (name);
ALTER TABLE Coin COMMENT = '货币表';