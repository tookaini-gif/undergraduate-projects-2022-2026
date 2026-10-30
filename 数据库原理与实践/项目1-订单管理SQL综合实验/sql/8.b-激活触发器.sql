-- MySQL has no ENABLE TRIGGER command. Exercise a trigger through its event.
START TRANSACTION;
UPDATE 客户 SET 状态=IF(状态='A','D','A') WHERE 编号=1;
SELECT * FROM 客户状态审计 ORDER BY 编号 DESC;
ROLLBACK;
