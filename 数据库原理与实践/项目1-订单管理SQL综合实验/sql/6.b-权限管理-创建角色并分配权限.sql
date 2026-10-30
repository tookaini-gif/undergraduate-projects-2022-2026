-- --------------------------------------------------
-- 权限管理-创建角色并分配权限
-- --------------------------------------------------
-- 创建角色
CREATE ROLE kaini_role;

-- 分配权限
GRANT SELECT, INSERT, UPDATE, DELETE ON undergraduate_orders_demo.* TO kaini_role;


