from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QTabWidget, QWidget,
                             QLabel, QLineEdit, QComboBox, QCheckBox, QMessageBox,
                             QHeaderView)
from PyQt5.QtCore import Qt
from typing import List
from models import DataManager, SchoolClass, Teacher, Course

class DataManagementDialog(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.dm = data_manager
        self.setWindowTitle("数据管理")
        self.resize(1100, 700)
        
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # Tab 1: Classes
        self.class_tab = QWidget()
        self.setup_class_tab() # Just sets up structure
        self.tabs.addTab(self.class_tab, "班级管理")
        
        # Tab 2: Teachers
        self.teacher_tab = QWidget()
        self.setup_teacher_tab()
        self.tabs.addTab(self.teacher_tab, "教师管理")
        
        # Tab 3: Courses
        self.course_tab = QWidget()
        self.setup_course_tab()
        self.tabs.addTab(self.course_tab, "课程管理")
        
        # Lazy Loading Logic
        self.loaded_tabs = set()
        self.tabs.currentChanged.connect(self.load_active_tab)
        
        self.layout.addWidget(self.tabs)
        
        # Initialize first tab
        self.load_active_tab(0)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("恢复默认")
        self.reset_btn.setStyleSheet("color: #e67e22;") # Subtle orange
        self.reset_btn.clicked.connect(self.restore_defaults)
        
        self.clear_btn = QPushButton("一键清空")
        self.clear_btn.setStyleSheet("color: #e74c3c;") # Red for danger
        self.clear_btn.clicked.connect(self.clear_all_data)
        
        self.import_btn = QPushButton("导入配置")
        self.import_btn.setStyleSheet("color: #27ae60;") # Green for import
        self.import_btn.clicked.connect(self.import_config)
        
        self.export_btn = QPushButton("导出当前配置")
        self.export_btn.setStyleSheet("color: #2e86de;") # Blue for export
        self.export_btn.clicked.connect(self.export_config)

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.apply_changes)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(btn_layout)

    def load_active_tab(self, index):
        if index in self.loaded_tabs:
            return
            
        self.setUpdatesEnabled(False)
        if index == 0: # Classes
            self.class_table.setRowCount(0)
            for c in self.dm.classes:
                self.add_class_row(c)
        elif index == 1: # Teachers
            self.teacher_table.setRowCount(0)
            for t in self.dm.teachers:
                self.add_teacher_row(t)
        elif index == 2: # Courses
            self.course_table.setSortingEnabled(False)
            self.course_table.setRowCount(0)
            sorted_courses = sorted(self.dm.courses, key=lambda x: (x.name, x.class_id))
            for co in sorted_courses:
                self.add_course_row(co)
            self.course_table.setSortingEnabled(True)
            
        self.loaded_tabs.add(index)
        self.setUpdatesEnabled(True)

    def setup_class_tab(self):
        layout = QVBoxLayout(self.class_tab)
        self.class_table = QTableWidget(0, 3)
        self.class_table.setHorizontalHeaderLabels(["ID", "班级名称", "年级"])
        self.class_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.class_table)
        
        btns = QHBoxLayout()
        add_btn = QPushButton("添加班级")
        add_btn.clicked.connect(lambda: self.add_class_row(SchoolClass(self.dm.generate_unique_id("C"), "", "")))
        del_btn = QPushButton("删除选中")
        del_btn.clicked.connect(lambda: self.class_table.removeRow(self.class_table.currentRow()))
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        layout.addLayout(btns)

    def add_class_row(self, c):
        row = self.class_table.rowCount()
        self.class_table.insertRow(row)
        self.class_table.setItem(row, 0, QTableWidgetItem(c.id))
        self.class_table.setItem(row, 1, QTableWidgetItem(c.name))
        self.class_table.setItem(row, 2, QTableWidgetItem(c.grade))

    def setup_teacher_tab(self):
        layout = QVBoxLayout(self.teacher_tab)
        self.teacher_table = QTableWidget(0, 6)
        self.teacher_table.setHorizontalHeaderLabels(["ID", "姓名", "学科", "授课年级(高一,高二)", "周最大课时", "不可排时间(逗号分隔)"])
        self.teacher_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.teacher_table)
        
        btns = QHBoxLayout()
        add_btn = QPushButton("添加教师")
        add_btn.clicked.connect(lambda: self.add_teacher_row(Teacher(self.dm.generate_unique_id("T"), "", "", 12, "", [])))
        del_btn = QPushButton("删除选中")
        del_btn.clicked.connect(lambda: self.teacher_table.removeRow(self.teacher_table.currentRow()))
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        layout.addLayout(btns)

    def add_teacher_row(self, t):
        row = self.teacher_table.rowCount()
        self.teacher_table.insertRow(row)
        self.teacher_table.setItem(row, 0, QTableWidgetItem(t.id))
        self.teacher_table.setItem(row, 1, QTableWidgetItem(t.name))
        self.teacher_table.setItem(row, 2, QTableWidgetItem(t.subject))
        self.teacher_table.setItem(row, 3, QTableWidgetItem(t.target_grades))
        self.teacher_table.setItem(row, 4, QTableWidgetItem(str(t.max_weekly)))
        self.teacher_table.setItem(row, 5, QTableWidgetItem(",".join(t.unavailable)))

    def setup_course_tab(self):
        layout = QVBoxLayout(self.course_tab)
        
        # Excel Tools
        excel_btns = QHBoxLayout()
        tpl_btn = QPushButton("下载 Excel 模板")
        tpl_btn.clicked.connect(self.download_template)
        import_btn = QPushButton("从 Excel 批量导入")
        import_btn.clicked.connect(self.import_excel)
        excel_btns.addWidget(tpl_btn)
        excel_btns.addWidget(import_btn)
        excel_btns.addStretch()
        layout.addLayout(excel_btns)

        self.course_table = QTableWidget(0, 7)
        self.course_table.setHorizontalHeaderLabels(["ID", "课程名", "教师名", "班级名", "周课时", "连堂", "时段"])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.course_table)
        
        btns = QHBoxLayout()
        add_btn = QPushButton("添加课程")
        add_btn.clicked.connect(lambda: self.add_course_row(Course(self.dm.generate_unique_id("CO"), "", "", "", 1, False, "standard")))
        del_btn = QPushButton("删除选中")
        del_btn.clicked.connect(lambda: self.course_table.removeRow(self.course_table.currentRow()))
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        layout.addLayout(btns)

    def add_course_row(self, co):
        row = self.course_table.rowCount()
        self.course_table.insertRow(row)
        self.course_table.setItem(row, 0, QTableWidgetItem(co.id))
        self.course_table.setItem(row, 1, QTableWidgetItem(co.name))
        
        # Teacher Dropdown - Show Name (ID)
        t_combo = QComboBox()
        t_combo.addItem("--- 请选择教师 ---", "")
        for t in self.dm.teachers:
            t_combo.addItem(f"{t.name} ({t.id})", t.id)
            if str(t.id).strip() == str(co.teacher_id).strip():
                t_combo.setCurrentText(f"{t.name} ({t.id})")
        self.course_table.setCellWidget(row, 2, t_combo)

        # Class Dropdown - Show Name (ID)
        c_combo = QComboBox()
        c_combo.addItem("--- 请选择班级 ---", "")
        for c in self.dm.classes:
            c_combo.addItem(f"{c.name} ({c.id})", c.id)
            if str(c.id).strip() == str(co.class_id).strip():
                c_combo.setCurrentText(f"{c.name} ({c.id})")
        self.course_table.setCellWidget(row, 3, c_combo)

        self.course_table.setItem(row, 4, QTableWidgetItem(str(co.weekly_hours)))
        self.course_table.setItem(row, 5, QTableWidgetItem("1" if co.consecutive else "0"))
        
        # Slot Type Dropdown
        st_combo = QComboBox()
        st_map = {"morning": "早自修", "standard": "正课", "evening": "晚自习"}
        for k, v in st_map.items():
            st_combo.addItem(v, k)
        st_current = getattr(co, "slot_type", "standard")
        st_combo.setCurrentText(st_map.get(st_current, "正课"))
        self.course_table.setCellWidget(row, 6, st_combo)

    def download_template(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存模板", "排课数据模板.xlsx", "Excel Files (*.xlsx)")
        if path:
            try:
                self.dm.generate_template(path)
                QMessageBox.information(self, "成功", f"模板已保存至：\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"生成失败：{e}")

    def import_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 Excel", "", "Excel Files (*.xlsx)")
        if path:
            try:
                self.dm.import_from_excel(path)
                QMessageBox.information(self, "成功", "数据导入成功！界面将自动刷新。")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败：{e}")

    def restore_defaults(self):
        reply = QMessageBox.warning(self, "确认恢复", "确定要恢复测试包配置吗？\n这将加载拥有 126 名老师、24 个班级的完整演示环境。", 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # Path to internal generator script
                # We assume the generator is accessible or we use a subprocess
                import subprocess
                # Search for the generator script in brain directory safely? 
                # Better yet: run the one we just edited in the project root if it exists
                gen_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_process.py") # placeholder
                # Actually, I will run the scratch script contents directly or via python command
                script_path = r"C:\Users\Lenovo\.gemini\antigravity\brain\3a2cc184-f215-431f-bd74-6e721d8ca256\scratch\generate_large_data.py"
                subprocess.run(["python", script_path], check=True)
                
                # Reload DataManager
                self.dm.load_all()
                QMessageBox.information(self, "成功", "测试数据已成功恢复！界面将自动刷新。")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"恢复失败：{e}")

    def clear_all_data(self):
        reply = QMessageBox.warning(self, "确认清空", "确认要清空当前所有教学数据（班级、教师、科目）吗？", 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.class_table.setRowCount(0)
            self.teacher_table.setRowCount(0)
            self.course_table.setRowCount(0)
            QMessageBox.information(self, "已清空", "临时列表已清空，点击保存后生效。")

    def _collect_ui_data(self):
        new_classes = []
        for r in range(self.class_table.rowCount()):
            id_item = self.class_table.item(r, 0)
            name_item = self.class_table.item(r, 1)
            if id_item and name_item and id_item.text():
                new_classes.append(SchoolClass(id_item.text(), name_item.text(), self.class_table.item(r, 2).text()))
        
        new_teachers = []
        for r in range(self.teacher_table.rowCount()):
            id_item = self.teacher_table.item(r, 0)
            name_item = self.teacher_table.item(r, 1)
            if id_item and name_item and id_item.text():
                unavail = self.teacher_table.item(r, 5).text().split(",") if self.teacher_table.item(r, 5) else []
                unavail = [u.strip() for u in unavail if u.strip()]
                new_teachers.append(Teacher(
                    id_item.text(), name_item.text(), 
                    self.teacher_table.item(r, 2).text(), 
                    int(self.teacher_table.item(r, 4).text()),
                    self.teacher_table.item(r, 3).text(),
                    unavail
                ))
        
        new_courses = []
        for r in range(self.course_table.rowCount()):
            id_item = self.course_table.item(r, 0)
            if id_item and id_item.text():
                t_combo = self.course_table.cellWidget(r, 2)
                c_combo = self.course_table.cellWidget(r, 3)
                st_combo = self.course_table.cellWidget(r, 6)
                
                new_courses.append(Course(
                    id_item.text().strip(), 
                    self.course_table.item(r, 1).text().strip(),
                    t_combo.currentData() if t_combo else "",
                    c_combo.currentData() if c_combo else "",
                    int(self.course_table.item(r, 4).text()),
                    self.course_table.item(r, 5).text() == "1",
                    st_combo.currentData() if st_combo else "standard"
                ))
        
        self.dm.classes = new_classes
        self.dm.teachers = new_teachers
        self.dm.courses = new_courses

    def apply_changes(self):
        try:
            self._collect_ui_data()
            self.dm.save_all()
            QMessageBox.information(self, "成功", "数据已保存！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败，请检查数据格式：{e}")

    def export_config(self):
        try:
            self._collect_ui_data()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"界面数据存在错误，请先修正：{e}")
            return
            
        import os
        import datetime
        from dataclasses import asdict
        import json
        from PyQt5.QtWidgets import QFileDialog
        
        # 默认保存路径为当前数据文件所在目录
        default_dir = os.path.abspath(os.path.dirname(self.dm.data_file))
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"排课配置导出_{timestamp}.json"
        default_path = os.path.join(default_dir, default_name)
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "导出当前配置",
            default_path,
            "JSON Data Files (*.json)"
        )
        
        if path:
            try:
                data = {
                    "classes": [asdict(c) for c in self.dm.classes],
                    "teachers": [asdict(t) for t in self.dm.teachers],
                    "courses": [asdict(co) for co in self.dm.courses],
                    "timetable": self.dm.timetable
                }
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", f"配置已成功导出至：\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败：{e}")

    def import_config(self):
        reply = QMessageBox.warning(self, "危险警告", "导入新配置文件将彻底覆盖当前系统中所有的基础数据及排课结果！\n\n强烈建议导入前先【导出当前配置】进行备份防丢！\n\n是否坚决继续导入？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
            
        import json
        from PyQt5.QtWidgets import QFileDialog
        from models import SchoolClass, Teacher, Course
        
        path, _ = QFileDialog.getOpenFileName(
            self, "选择欲导入的配置文件", "", "JSON Data Files (*.json)"
        )
        
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 校验包含基本的数据骨架
                if "classes" not in data or "teachers" not in data or "courses" not in data:
                    raise ValueError("所选文件并非合法的排课系统配置快照包。")
                    
                self.dm.classes = [SchoolClass(**c) for c in data["classes"]]
                self.dm.teachers = [Teacher(**t) for t in data["teachers"]]
                self.dm.courses = [Course(**co) for co in data["courses"]]
                self.dm.timetable = data.get("timetable", {})
                
                # 执行硬性写入覆盖
                self.dm.save_all()
                QMessageBox.information(self, "合并成功", "新课表配置已火速导入并更迭完成。\n主界面即将自动为您刷新全局排课视图！")
                self.accept() # 关闭弹窗引发 main.py 重载
            except Exception as e:
                QMessageBox.critical(self, "解析错误", f"配置文件导入失败，核心引擎拒绝了本次损毁文件：\n{e}")

class CourseSelectionDialog(QDialog):
    def __init__(self, courses: List[Course], current_course_id: str = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择课程")
        self.setFixedWidth(400)
        self.selected_course_id = current_course_id
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("请为当前时段选择课程:"))
        
        self.combo = QComboBox()
        self.combo.addItem("--- 空白 (删除课程) ---", None)
        
        # Mapping slot_type to Chinese
        st_map = {"morning": "早自习", "standard": "正课", "evening": "晚自习"}
        
        for idx, course in enumerate(courses):
            type_str = st_map.get(course.slot_type, "未知")
            self.combo.addItem(f"[{type_str}] {course.name} ({course.id})", course.id)
            if course.id == current_course_id:
                self.combo.setCurrentIndex(idx + 1)
        
        layout.addWidget(self.combo)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept_selection)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def accept_selection(self):
        self.selected_course_id = self.combo.currentData()
        self.accept()

class HistoryDialog(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.dm = data_manager
        self.setWindowTitle("项目历史纪录 (快照)")
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["生成时间", "备注名称"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.history_data = self.dm.get_history_list()
        for idx, item in enumerate(self.history_data):
            self.table.insertRow(idx)
            self.table.setItem(idx, 0, QTableWidgetItem(item["timestamp"]))
            self.table.setItem(idx, 1, QTableWidgetItem(item["name"]))
            
        layout.addWidget(self.table)
        
        btns = QHBoxLayout()
        restore_btn = QPushButton("恢复到此版本")
        restore_btn.clicked.connect(self.do_restore)
        cancel_btn = QPushButton("关闭")
        cancel_btn.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(restore_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def do_restore(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个版本。")
            return
            
        item = self.history_data[row]
        reply = QMessageBox.question(self, "确认恢复", f"确定要恢复到版本 [{item['name']}] 吗？\n当前未保存的更改将丢失。",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.dm.restore_snapshot(item["filename"]):
                QMessageBox.information(self, "成功", "历史版本已恢复！")
                self.accept()

class TeacherStatisticsDialog(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.dm = data_manager
        self.setWindowTitle("教师排课负载统计")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Calculate stats
        stats = self.calculate_stats()
        
        self.table = QTableWidget(len(stats), 6)
        self.table.setHorizontalHeaderLabels(["姓名", "科目", "正课 (节)", "早自习 (节)", "晚自习 (节)", "合计 (节)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(False) # DISABLE sorting during population to prevent cell scrambling!
        
        for i, (t_id, data) in enumerate(stats.items()):
            teacher = self.dm.get_teacher_by_id(t_id)
            name = teacher.name if teacher else t_id
            subject = teacher.subject if teacher else ""
            
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(subject))
            self.table.setItem(i, 2, QTableWidgetItem(str(data["standard"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(data["morning"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(data["evening"])))
            self.table.setItem(i, 5, QTableWidgetItem(str(data["total"])))
            
        self.table.setSortingEnabled(True) # Re-enable sorting after data is safely populated
        layout.addWidget(self.table)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def calculate_stats(self):
        # Initialize with every single teacher from DataManager to ensure none are missing
        # Format: {teacher_id: {morning: 0, standard: 0, evening: 0, total: 0}}
        stats = {}
        for t in self.dm.teachers:
            safe_id = str(t.id).strip()
            stats[safe_id] = {"morning": 0, "standard": 0, "evening": 0, "total": 0}
        
        m_p = self.dm.morning_count
        s_p = self.dm.standard_count
        # e_p = self.dm.evening_count
        
        for c_id, grid in self.dm.timetable.items():
            for p_idx, row in enumerate(grid):
                for d_idx, item in enumerate(row):
                    course_id = None
                    if isinstance(item, dict):
                        course_id = item.get("course_id")
                    elif isinstance(item, str):
                        course_id = item
                    
                    if course_id:
                        course = self.dm.get_course_by_id(course_id)
                        if course:
                            # Use robust ID matching
                            t_id = str(course.teacher_id).strip()
                            if t_id in stats:
                                st = getattr(course, "slot_type", "standard")
                                if st in stats[t_id]:
                                    stats[t_id][st] += 1
                                else:
                                    # Fallback index mapping
                                    if p_idx < m_p: stats[t_id]["morning"] += 1
                                    elif p_idx < m_p + s_p: stats[t_id]["standard"] += 1
                                    else: stats[t_id]["evening"] += 1
                                
                                stats[t_id]["total"] += 1
        return stats
