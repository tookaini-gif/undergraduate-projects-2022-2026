-- --------------------------------------------------
-- 权限管理-收回权限
-- --------------------------------------------------
-- 收回直接分配权限
REVOKE SELECT, INSERT, UPDATE, DELETE ON undergraduate_orders_demo.* FROM 'kaini'@'localhost';

-- 收回通过角色分配权限
REVOKE kaini_role FROM 'kaini'@'localhost';



