create table Coin
(
  id          int auto_increment
    primary key,
  name        varchar(20)                    not null
  comment '名称',
  full_name   varchar(255)                   null
  comment '全称',
  price       double(7, 5) default '1.00000' null
  comment '上一次通知价格(美元)',
  update_time datetime                       null
  comment '更新时间',
  constraint Coin_name_uindex
  unique (name)
)
  comment '货币表';

# insert what Coin you like
INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`) VALUES ('eos', 'EOS', 'EOS', 1, '2018-06-30 15:43:55');
INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`) VALUES ('binance-coin', 'Binance Coin', 'BNB', DEFAULT, '2018-06-30 15:52:42');
INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`) VALUES ('ripple', 'XRP', 'XRP', 1, '2018-06-30 15:48:40');

