-- --------------------------------------------------
-- 权限管理-给用户分配权限（直接分配、通过角色分配）
-- --------------------------------------------------
-- 直接分配
GRANT SELECT, INSERT, UPDATE, DELETE ON undergraduate_orders_demo.* TO 'kaini'@'localhost';

-- 通过角色分配
GRANT kaini_role TO 'kaini'@'localhost';



SET DEFAULT ROLE kaini_role TO 'kaini'@'localhost';
