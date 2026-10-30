-- Teardown for the dedicated demo schema only; child tables before parents.
DROP VIEW IF EXISTS 出货单视图, 产品价格视图;
DROP TABLE IF EXISTS 订单细节, 订单, 产品, 客户;
