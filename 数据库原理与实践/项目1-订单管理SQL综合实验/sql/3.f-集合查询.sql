-- UNION removes duplicate rows.
SELECT 产品编号, 时价 FROM 订单细节
UNION
SELECT 产品编号, 单价 FROM 产品;
-- Intersection using EXISTS (compatible with MySQL 8.0 before INTERSECT).
SELECT DISTINCT d.产品编号, d.时价 FROM 订单细节 d
WHERE EXISTS (SELECT 1 FROM 产品 p WHERE p.产品编号=d.产品编号 AND p.单价=d.时价);
-- Set difference using NOT EXISTS.
SELECT DISTINCT d.产品编号, d.时价 FROM 订单细节 d
WHERE NOT EXISTS (SELECT 1 FROM 产品 p WHERE p.产品编号=d.产品编号 AND p.单价=d.时价);
