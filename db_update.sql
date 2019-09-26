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
INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`)
VALUES ('eos', 'EOS', 'EOS', 1, '2018-06-30 15:43:55');
INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`)
VALUES ('binance-coin', 'Binance Coin', 'BNB', DEFAULT, '2018-06-30 15:52:42');
INSERT INTO `ICO`.`Coin` (`id`, `name`, `sample_name`, `price`, `update_time`)
VALUES ('ripple', 'XRP', 'XRP', 1, '2018-06-30 15:48:40');

ALTER TABLE Coin
    ADD lian_xu int DEFAULT 0 NULL COMMENT '连续涨跌次数';

CREATE TABLE attribute
(
    name               varchar(200) PRIMARY KEY COMMENT '货币全称',
    sample_name        varchar(10) COMMENT '简写',
    coinmarketcap_id   varchar(200) COMMENT 'coinmarketcap 平台 id',
    coinmarketcap_rank int(3) COMMENT 'coinmarketcap 平台排名',
    otcbtc_id          varchar(20) COMMENT 'otcbtc 平台 id',
    otcbtc_ticker_id   varchar(20) COMMENT 'otcbtc 平台 ticker id'
);
ALTER TABLE attribute
    COMMENT = '各平台属性对照表';

drop table if exists autotrade.strategy_low_buy_high_sell_max;
create table autotrade.strategy_low_buy_high_sell_max
(
    id              int auto_increment,
    symbol          varchar(15)                                                           not null,
    coin_name       varchar(11)                                                           not null,
    platform        varchar(15)                                                           not null,
    max_price       decimal(18, 10) default 0                                             not null,
    min_price       decimal(18, 10) default 0                                             not null,
    reminder_point  float(4, 3)     default 0.007                                         not null comment '提醒百分比：每涨跌该值时进行提醒',
    count_in_a_row  int(3)          default 0                                             not null comment '连续次数',
    trade_spend     decimal(18, 10) default 0                                             not null comment '上次交易实际金额：通过交易后余额与交易前余额做差',
    trade_quantity  decimal(18, 10) default 0                                             not null comment '上次交易实际数量，通过交易后余额与交易前余额做差',
    trade_avg_price decimal(18, 10) default 0                                             not null comment '上次交易均价：实际交易金额/实际交易数量',
    trade_side      varchar(4)      default ''                                            not null comment '交易方向：buy 或 sell',
    enabled         tinyint(1)      default 0                                             not null comment '上次交易订单号',
    last_order_id   int             default 0                                             not null,
    create_time     datetime        default CURRENT_TIMESTAMP                             not null,
    update_time     datetime        default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP not null,
    constraint strategy_low_buy_high_sell_max_pk
        primary key (id)
);
