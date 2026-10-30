-- --------------------------------------------------
-- 权限管理-验证权限分配正确性
-- --------------------------------------------------
-- 数据库使用 SHOW GRANTS
SHOW GRANTS;
SHOW GRANTS FOR 'kaini'@'localhost';

-- 查询MySQL系统表
SELECT * FROM mysql.user WHERE User = 'kaini';
SELECT * FROM mysql.db WHERE User = 'kaini' AND Host = 'localhost';




