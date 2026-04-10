import json
import os
from models import DataManager
from scheduler import Scheduler

def check_stats():
    dm = DataManager("data.json", "settings.json")
    print(f"Loaded {len(dm.teachers)} teachers, {len(dm.classes)} classes, {len(dm.courses)} courses")
    
    scheduler = Scheduler(dm)
    print("Running scheduler...")
    try:
        success = scheduler.schedule()
        print(f"Schedule success: {success}")
        dm.timetable = scheduler.get_result()
    except Exception as e:
        print(f"Schedule failed: {e}")
        return

    # Simulate dialogs' calculate_stats logic verbatim
    stats = {}
    for t in dm.teachers:
        safe_id = str(t.id).strip()
        stats[safe_id] = {"morning": 0, "standard": 0, "evening": 0, "total": 0, "name": t.name}
    
    m_p = dm.morning_count
    s_p = dm.standard_count
    
    for c_id, grid in dm.timetable.items():
        for p_idx, row in enumerate(grid):
            for d_idx, item in enumerate(row):
                course_id = None
                if isinstance(item, dict):
                    course_id = item.get("course_id")
                elif isinstance(item, str):
                    course_id = item
                
                if course_id:
                    course = dm.get_course_by_id(course_id)
                    if course:
                        t_id = str(course.teacher_id).strip()
                        if t_id in stats:
                            st = getattr(course, "slot_type", "standard")
                            if st in stats[t_id]:
                                stats[t_id][st] += 1
                            else:
                                if p_idx < m_p: stats[t_id]["morning"] += 1
                                elif p_idx < m_p + s_p: stats[t_id]["standard"] += 1
                                else: stats[t_id]["evening"] += 1
                            stats[t_id]["total"] += 1

    # Print top 10 teachers
    active_teachers = [v for k, v in stats.items() if v["total"] > 0]
    print(f"Teachers with >0 total stats: {len(active_teachers)} / {len(stats)}")
    
    empty_teachers = [v["name"] for k, v in stats.items() if v["total"] == 0]
    print(f"Sample of empty teachers: {empty_teachers[:10]}")
    
if __name__ == "__main__":
    check_stats()
