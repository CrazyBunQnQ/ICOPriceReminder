CREATE DATABASE if not exists `autotrade` DEFAULT CHARACTER SET = `utf8mb4`;

drop table if exists autotrade.account;
create table if not exists autotrade.account
(
    id          int auto_increment,
    platform    varchar(15)                                                           not null,
    usdt        decimal(18, 10) default 0.0000000000                                  not null comment 'usdt  count',
    usdt_locked decimal(18, 10) default 0.0000000000                                  not null,
    btc         decimal(18, 10) default 0.0000000000                                  not null comment 'btc count',
    btc_locked  decimal(18, 10) default 0.0000000000                                  not null,
    eth         decimal(18, 10) default 0.0000000000                                  not null comment 'eth count',
    eth_locked  decimal(18, 10) default 0.0000000000                                  not null,
    bnb         decimal(18, 10) default 0.0000000000                                  not null comment 'bnb count',
    bnb_locked  decimal(18, 10) default 0.0000000000                                  not null,
    eos         decimal(18, 10) default 0.0000000000                                  not null comment 'eos count',
    eos_locked  decimal(18, 10) default 0.0000000000                                  not null,
    xrp         decimal(18, 10) default 0.0000000000                                  not null comment 'xrp count',
    xrp_locked  decimal(18, 10) default 0.0000000000                                  not null,
    cur_profit  decimal(18, 10) default 0                                             not null comment '当前盈利金额(RMB)',
    create_time timestamp       default CURRENT_TIMESTAMP                             not null,
    update_time timestamp       default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP not null,
    constraint account_pk
        primary key (id),
    constraint account_platform_uindex
        unique (platform)
)
    comment 'account status';

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
create table if not exists autotrade.strategy_low_buy_high_sell_max
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

drop table if exists autotrade.trade_history;
create table if not exists autotrade.trade_history
(
    id          int auto_increment,
    symbol      varchar(15)                                                    not null,
    platform    varchar(15)                                                    not null,
    order_id    int      default 0                                             not null,
    volume      decimal(18, 10)                                                not null comment '成交总额',
    quantity    decimal(18, 10)                                                not null comment '成交量',
    price       decimal(18, 10)                                                not null comment '成交均价',
    side        varchar(4)                                                     not null comment 'buy 或 sell',
    create_time datetime default CURRENT_TIMESTAMP                             not null comment '下单时间',
    finish_time datetime default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP not null comment '完成时间',
    update_time datetime default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP not null,
    constraint trade_history_pk
        primary key (id)
);
# ([buysell]{3,4}) ([a-z]+)\s+.*\s+.*\s+.*\s+.*\s+(\d{2}:\d{2}) (\d{2})/(\d{2})\s+.*\s+.*\s+.*\s+.*\s+.*\s+(\d+\.?\d+)\s+(\d+\.?\d+)\n(\d+\.?\d+)
# INSERT INTO autotrade.trade_history \(id, symbol, platform, volume, quantity, price, side, create_time, finish_time, update_time\) VALUES \(1, '$2', 'huobi', $6, $8, $7, '$1', '2019-$4-$5 $3:00', '2019-$4-$5 $3:00', DEFAULT\);

# (\d{2}):(\d{2}) (\d{2})/(\d{2})\s+(\d+\.\d+) (\w+)\s+(\d+\.\d+) (\w+)\s+(\d+\.\d+) (\w+)\s+(\d+\.\d+) (\w+)\s+(\d+\.\d+) (\w+)
# INSERT INTO autotrade.trade_history \(id, symbol, platform, volume, quantity, price, side, create_time, finish_time, update_time\) VALUES \(1, '$2', 'huobi', $6, $8, $7, '$1', '2019-$4-$5 $3:00', '2019-$4-$5 $3:00', DEFAULT\);

drop table if exists autotrade.profit_amount;
create table if not exists profit_amount
(
    id            int auto_increment,
    platform      varchar(15)                                                           not null,
    usdt          decimal(18, 10) default 0                                             not null,
    usdt_rmb      float(8, 6)     default 7.0                                           not null comment 'usdt rate',
    btc           decimal(18, 10) default 0                                             not null,
    btc_usdt      decimal(18, 10) default 0                                             not null,
    eth           decimal(18, 10) default 0                                             not null,
    eth_usdt      decimal(18, 10) default 0                                             not null,
    eos           decimal(18, 10) default 0                                             not null,
    eos_usdt      decimal(18, 10) default 0                                             not null,
    xrp           decimal(18, 10) default 0                                             not null,
    xrp_usdt      decimal(18, 10) default 0                                             not null,
    profit_amount decimal(18, 10) default 0                                             not null,
    create_time   datetime        default CURRENT_TIMESTAMP                             not null,
    update_time   datetime        default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP not null,
    constraint profit_amount_pk
        primary key (id)
)
    comment '收益历史';

create unique index profit_amount_platform_uindex
    on profit_amount (platform);

