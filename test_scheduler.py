import time
import sys
from models import DataManager, Course, Teacher, SchoolClass
from scheduler import Scheduler

def test_infinite_loop_bug():
    print("正在构造极端排课冲突数据（复现卡死 Bug）...")
    dm = DataManager()
    
    # 模拟极端情况：一天8节课，一周5天 = 40节。
    # 我们创建一个老师，给他安排50节课（超过容量且违背硬约束）
    t = Teacher("t1", "王老师", "数学", max_weekly=50, unavailable=[])
    c = SchoolClass("c1", "高一1班", "高一")
    dm.teachers.append(t)
    dm.classes.append(c)
    
    # 添加极其密集的课程
    co1 = Course("co1", "数学主课", "t1", "c1", weekly_hours=45, consecutive=False)
    dm.courses.append(co1)
    
    scheduler = Scheduler(dm)
    
    print("开始排课算法（预期将陷入无限死循环或耗时极长）...")
    start_time = time.time()
    
    # 如果算法没有超时机制，这里将卡死
    try:
        scheduler.schedule()
        duration = time.time() - start_time
        print(f"排课结束，耗时: {duration:.2f} 秒")
    except KeyboardInterrupt:
        print("\n测试被强制中断：证实存在死循环/超时问题。")

if __name__ == "__main__":
    test_infinite_loop_bug()
