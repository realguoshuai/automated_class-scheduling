import random
import sys
from typing import List, Dict, Tuple, Optional, Any
from models import DataManager, Course, Teacher, SchoolClass

# For deep backtracking in saturated cases
sys.setrecursionlimit(10000)

class Scheduler:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager
        
        # Internal state for backtracking
        self.timetable = {}  # {class_id: [[None]*days for _ in range(periods)]}
        self.teacher_occupied = {}  # {teacher_id: set of (day, period)}
        self.class_occupied = {}  # {class_id: set of (day, period)}
        self.max_iterations = 2000000
        self.iterations = 0
        self.fail_counts = {} # {course_id: count}
        self.teacher_daily_load = {} # {teacher_id: {day: count}}
        self.teacher_limits = {} # {teacher_id: max_per_day}

    def reset_state(self):
        self.timetable = {c.id: [[None for _ in range(self.days)] for _ in range(self.periods)] for c in self.dm.classes}
        self.teacher_occupied = {t.id: set() for t in self.dm.teachers}
        self.class_occupied = {c.id: set() for c in self.dm.classes}
        self.teacher_daily_load = {t.id: {d: 0 for d in range(self.days)} for t in self.dm.teachers}
        
        # Calculate dynamic limits for teachers: (avg per day) + 2 buffer
        for t in self.dm.teachers:
            # Note: max_weekly here is the total workload assigned to them
            limit = (t.max_weekly // self.days) + 2
            self.teacher_limits[t.id] = max(1, limit)
        
        # Pre-fill teacher unavailable times
        for t in self.dm.teachers:
            for unauth in t.unavailable:
                try:
                    # Parse "周一第1节" -> day=0, period=0
                    day_str = unauth[1]
                    period_str = unauth[unauth.find("第")+1:-1]
                    day_map = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6}
                    d = day_map.get(day_str, 0)
                    p = int(period_str) - 1
                    if 0 <= d < self.days and 0 <= p < self.periods:
                        self.teacher_occupied[t.id].add((d, p))
                except Exception:
                    continue

    def schedule(self) -> bool:
        # Refresh settings
        self.days = self.dm.settings["days_per_week"]
        self.m_p = self.dm.morning_count
        self.s_p = self.dm.standard_count
        self.e_p = self.dm.evening_count
        self.periods = self.dm.total_periods
        
        self.morning_end = self.m_p + (self.s_p // 2)
        self.consecutive_starts = self.dm.settings.get("consecutive_allowed_starts", [1, 3, 5, 7])
        self.std_consec_starts = [s + self.m_p - 1 for s in self.consecutive_starts]
        
        last_error_msg = ""
        max_attempts = 30 # For two-pass, we can do fewer attempts per phase but more restarts
        
        for attempt in range(max_attempts):
            self.iterations = 0
            self.fail_counts = {}
            if self._do_two_pass_schedule(attempt):
                return True
            
            if self.fail_counts:
                top_fail_id = max(self.fail_counts, key=self.fail_counts.get)
                course = self.dm.get_course_by_id(top_fail_id)
                teacher = self.dm.get_teacher_by_id(course.teacher_id) if course else None
                main_failure = f"{course.name if course else top_fail_id} ({teacher.name if teacher else '未知'})"
                last_error_msg = f"排课冲突：尝试了 {max_attempts} 轮随机搜索仍未找到完美解。\n瓶颈：{main_failure}"

        raise Exception(last_error_msg if last_error_msg else "排课失败：约束过于苛刻，无法找到可行解。")

    def _do_two_pass_schedule(self, attempt_idx: int) -> bool:
        self.reset_state()
        
        # Phase 1: Standard Courses Skeleton (Total 40 slots)
        std_consec = []
        std_normal = []
        for course in self.dm.courses:
            if course.slot_type == "standard":
                remaining = course.weekly_hours
                if course.consecutive:
                    while remaining >= 2:
                        std_consec.append({"course": course, "is_consecutive": True})
                        remaining -= 2
                while remaining > 0:
                    std_normal.append({"course": course, "is_consecutive": False})
                    remaining -= 1
        
        phase_1_tasks = std_consec + std_normal
        # MRV Heuristic: Fill Class-by-Class first, then prioritize Consecutive blocks within the class, then by weekly_hours
        phase_1_tasks.sort(key=lambda t: (t["course"].class_id, not t["is_consecutive"], -t["course"].weekly_hours))
        
        self.max_iterations = 200000
        if not self._backtrack(phase_1_tasks, 0):
            return False
            
        # Phase 2: Duty/Study Sessions (Total 20 slots)
        # These are much easier because they are restricted to specific rows
        duty_tasks = []
        for course in self.dm.courses:
            if course.slot_type != "standard":
                remaining = course.weekly_hours
                while remaining > 0:
                    duty_tasks.append({"course": course, "is_consecutive": False})
                    remaining -= 1
        
        # MRV Heuristic for Phase 2: Place larger duty blocks first
        duty_tasks.sort(key=lambda t: t["course"].weekly_hours, reverse=True)
        self.max_iterations = 300000 # Shared iterations pool or reset? Let's reset.
        return self._backtrack(duty_tasks, 0)

    def _backtrack(self, tasks: List[dict], index: int) -> bool:
        self.iterations += 1
        if self.iterations > self.max_iterations:
            return False

        if index == len(tasks):
            return True
        
        task = tasks[index]
        course = task["course"]
        is_consecutive = task["is_consecutive"]
        
        # Get candidate slots
        slots = self._get_candidate_slots(course, is_consecutive)
        
        for d, p in slots:
            if is_consecutive:
                if p + 1 < self.periods and self._can_place_consecutive(course, d, p):
                    self._place(course, d, p)
                    self._place(course, d, p + 1)
                    if self._backtrack(tasks, index + 1):
                        return True
                    self._unplace(course, d, p)
                    self._unplace(course, d, p + 1)
            else:
                if self._can_place_single(course, d, p):
                    self._place(course, d, p)
                    if self._backtrack(tasks, index + 1):
                        return True
                    self._unplace(course, d, p)
        
        # If we reach here, this task failed to find a slot
        self.fail_counts[course.id] = self.fail_counts.get(course.id, 0) + 1
        return False

    def _get_candidate_slots(self, course: Course, is_consecutive: bool) -> List[Tuple[int, int]]:
        candidates = []
        
        # Define search range based on slot_type
        if course.slot_type == "morning":
            p_range = range(0, self.m_p)
        elif course.slot_type == "evening":
            p_range = range(self.m_p + self.s_p, self.periods)
        else: # standard
            p_range = range(self.m_p, self.m_p + self.s_p)
            
        for d in range(self.days):
            for p in p_range:
                if is_consecutive:
                    if p in self.std_consec_starts:
                        candidates.append((d, p))
                else:
                    candidates.append((d, p))
        
        # Fast randomization to avoid local deadlocks
        random.shuffle(candidates)
            
        return candidates

    def _can_place_single(self, course: Course, d: int, p: int) -> bool:
        if (d, p) in self.teacher_occupied[course.teacher_id]:
            return False
        if (d, p) in self.class_occupied[course.class_id]:
            return False
            
        # Hard Pruning: Teacher Fatigue Control (Daily limit)
        if self.teacher_daily_load[course.teacher_id][d] >= self.teacher_limits.get(course.teacher_id, 8):
            return False

        return True

    def _can_place_consecutive(self, course: Course, d: int, p: int) -> bool:
        # Check if both slots are within the same type range to avoid crossing (e.g. morning to standard)
        if course.slot_type == "morning":
            if p + 1 >= self.m_p: return False
        elif course.slot_type == "standard":
            if p + 1 >= self.m_p + self.s_p: return False
        
        return self._can_place_single(course, d, p) and self._can_place_single(course, d, p + 1)

    def _place(self, course: Course, d: int, p: int):
        self.timetable[course.class_id][p][d] = course.id
        self.teacher_occupied[course.teacher_id].add((d, p))
        self.class_occupied[course.class_id].add((d, p))
        self.teacher_daily_load[course.teacher_id][d] += 1

    def _unplace(self, course: Course, d: int, p: int):
        self.timetable[course.class_id][p][d] = None
        self.teacher_occupied[course.teacher_id].discard((d, p))
        self.class_occupied[course.class_id].discard((d, p))
        self.teacher_daily_load[course.teacher_id][d] -= 1

    def get_result(self) -> Dict[str, List[List[Dict]]]:
        result = {}
        for class_id, grid in self.timetable.items():
            formatted_grid = []
            for p in range(self.periods):
                row = []
                for d in range(self.days):
                    course_id = grid[p][d]
                    if course_id:
                        course = self.dm.get_course_by_id(course_id)
                        teacher = self.dm.get_teacher_by_id(course.teacher_id) if course else None
                        row.append({
                            "course_id": course_id, 
                            "name": course.name if course else "Unknown",
                            "teacher_name": teacher.name if teacher else ""
                        })
                    else:
                        row.append({"course_id": None, "name": "", "teacher_name": ""})
                formatted_grid.append(row)
            result[class_id] = formatted_grid
        return result
