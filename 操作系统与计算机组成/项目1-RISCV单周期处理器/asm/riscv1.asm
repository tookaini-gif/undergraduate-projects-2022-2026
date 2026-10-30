.data
array: .word 5, 3, 4, 1, 2  # 初始化一个包含5个整数的数组

.text
main:
    la t0, array       # 将数组地址加载到寄存器 t0
    li t1, 4           # 设置外循环的计数器（数组长度减1）

outer_loop:
    beqz t1, end_sort  # 如果计数器为0，则排序结束
    li t2, 0           # 设置内循环的计数器

inner_loop:
    bge t2, t1, update_outer # 如果内循环计数器 >= 外循环计数器，则更新外循环计数器
    slli t3, t2, 2     # 计算当前元素的偏移量（t2 * 4）
    add t4, t0, t3     # 计算当前元素的地址
    lw t5, 0(t4)       # 加载当前元素
    lw t6, 4(t4)       # 加载下一个元素
    ble t5, t6, skip_swap # 如果当前元素 <= 下一个元素，则跳过交换
    sw t5, 4(t4)       # 否则，交换元素
    sw t6, 0(t4)

skip_swap:
    addi t2, t2, 1     # 内循环计数器加1
    j inner_loop       # 跳转到内循环的开始

update_outer:
    addi t1, t1, -1    # 外循环计数器减1
    j outer_loop       # 跳转到外循环的开始

end_sort:
    # 排序完成，此处可以添加代码来验证排序结果或退出程序
    li a7, 10          # 系统调用号 10 (exit)
    ecall              # 执行系统调用以退出程序
