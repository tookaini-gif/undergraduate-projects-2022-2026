-- Separate disposable tables keep this exercise independent of base-table changes.
DROP TABLE IF EXISTS 约束订单, 约束客户;
CREATE TABLE 约束客户 (编号 INT PRIMARY KEY, 名称 VARCHAR(100) NOT NULL);
CREATE TABLE 约束订单 (
    编号 INT PRIMARY KEY,
    客户编号 INT NOT NULL,
    金额 DECIMAL(10,2) NOT NULL,
    CONSTRAINT 约束外键 FOREIGN KEY (客户编号) REFERENCES 约束客户(编号),
    CONSTRAINT 金额检查 CHECK (金额>=0)
);
INSERT INTO 约束客户 VALUES (1,'约束演示客户（虚构）');
INSERT INTO 约束订单 VALUES (1,1,10.00);
-- Optional negative tests, execute separately and expect failure:
-- INSERT INTO 约束订单 VALUES (1,1,10.00); -- duplicate primary key
-- INSERT INTO 约束订单 VALUES (2,999,10.00); -- nonexistent customer
-- INSERT INTO 约束订单 VALUES (2,1,-1.00); -- negative amount
