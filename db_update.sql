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

delete from Coin;

ALTER TABLE Coin MODIFY id varchar(20) NOT NULL COMMENT '货币 ID';
DROP INDEX Coin_name_uindex ON Coin;
ALTER TABLE Coin MODIFY name varchar(255) NOT NULL COMMENT '货币名称';
ALTER TABLE Coin CHANGE full_name sample_name varchar(10) COMMENT '简称';
ALTER TABLE Coin DROP PRIMARY KEY;
ALTER TABLE Coin ADD PRIMARY KEY (id);

ALTER TABLE Coin MODIFY name varchar(255) COMMENT '货币名称';
ALTER TABLE Coin MODIFY sample_name varchar(10) NOT NULL COMMENT '简称';

INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`) VALUES ('eos', 'EOS', 'EOS', 1, '2018-06-30 15:43:55');
INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`) VALUES ('binance-coin', 'Binance Coin', 'BNB', DEFAULT, '2018-06-30 15:52:42');
INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`) VALUES ('ripple', 'XRP', 'XRP', 1, '2018-06-30 15:48:40');