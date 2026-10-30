-- Joined shipment view is used for reading only.
SELECT * FROM 出货单视图 WHERE 客户名称 = '示例客户01（虚构）';
-- A single-table view demonstrates predictable updatable-view semantics.
CREATE OR REPLACE VIEW 产品价格视图 AS SELECT 产品编号, 产品名称, 单价 FROM 产品;
UPDATE 产品价格视图 SET 产品名称 = '示例大纽扣' WHERE 产品编号 = 'P-10';
SELECT * FROM 产品价格视图 WHERE 产品编号 = 'P-10';
