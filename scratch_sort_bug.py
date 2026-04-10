import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem

def test_sort_bug():
    app = QApplication(sys.argv)
    table = QTableWidget(5, 2)
    table.setSortingEnabled(True) # ENABLE BEFORE INSERTION
    
    data = [
        ("C", "10"),
        ("A", "20"),
        ("E", "30"),
        ("B", "40"),
        ("D", "50")
    ]
    
    for i, (name, val) in enumerate(data):
        table.setItem(i, 0, QTableWidgetItem(name))
        # After inserting column 0, the table sorts!
        # "A" will move to row 0. We are at i=1.
        # Now we insert "20" into row 1, col 1. But row 1 is now "C"! So "C" gets "20"!
        table.setItem(i, 1, QTableWidgetItem(val))
        
    for r in range(5):
        c0 = table.item(r, 0).text() if table.item(r, 0) else "None"
        c1 = table.item(r, 1).text() if table.item(r, 1) else "None"
        print(f"Row {r}: {c0} - {c1}")

if __name__ == "__main__":
    test_sort_bug()
