-- --------------------------------------------------
-- 权限管理-创建用户
-- --------------------------------------------------
CREATE USER 'kaini'@'localhost' IDENTIFIED BY 'ChangeMe_DemoOnly!2026';

SELECT * FROM mysql.user WHERE User = 'kaini';

