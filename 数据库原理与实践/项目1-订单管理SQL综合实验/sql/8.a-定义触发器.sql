-- MySQL triggers are enabled immediately after creation.
CREATE TABLE IF NOT EXISTS 客户状态审计 (
    编号 INT AUTO_INCREMENT PRIMARY KEY,
    客户编号 VARCHAR(20), 旧状态 VARCHAR(1), 新状态 VARCHAR(1),
    发生时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
DROP TRIGGER IF EXISTS customer_status_audit;
DELIMITER $$
CREATE TRIGGER customer_status_audit AFTER UPDATE ON 客户
FOR EACH ROW
BEGIN
    IF NOT (OLD.状态 <=> NEW.状态) THEN
        INSERT INTO 客户状态审计(客户编号,旧状态,新状态)
        VALUES(NEW.客户编号,OLD.状态,NEW.状态);
    END IF;
END$$
DELIMITER ;
