"""
PlanRail CP-SAT Maintenance Block Optimizer Unit Tests
======================================================

Tests all 10 core constraints and objective behaviors of the CP-SAT solver.
"""

import unittest
from datetime import date

from app.optimizer.solver import (
    MaintenanceBlockSolver,
    MaintenanceRequestInput,
    MaintenanceWindowInput,
)


class TestMaintenanceBlockSolver(unittest.TestCase):
    def setUp(self):
        self.solver = MaintenanceBlockSolver(time_limit_seconds=3.0, random_seed=42)
        self.target_date = date(2026, 9, 10)

    def test_01_basic_scheduling(self):
        """Test 1: One maintenance task + one feasible window -> Task scheduled."""
        req = MaintenanceRequestInput(
            id=1,
            request_id="MR001",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=2.0,
            priority_score=80.0,
        )
        win = MaintenanceWindowInput(
            id=101,
            window_id="MW01",
            section_id="SEC_A",
            start_hour=2,
            duration_minutes=240,
            is_feasible=True,
            traffic_level="LOW",
        )
        result = self.solver.solve(
            requests=[req],
            windows=[win],
            target_date=self.target_date,
        )
        self.assertIn(result.status, ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(result.scheduled_task_ids, ["MR001"])
        self.assertEqual(len(result.blocks), 1)
        self.assertEqual(result.blocks[0].tasks[0].request_id, "MR001")

    def test_02_duration_constraint(self):
        """Test 2: Task duration (5 hrs = 300 mins) > window capacity (180 mins) -> Task unscheduled."""
        req = MaintenanceRequestInput(
            id=1,
            request_id="MR_LONG",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=5.0,
            priority_score=90.0,
        )
        win = MaintenanceWindowInput(
            id=101,
            window_id="MW01",
            section_id="SEC_A",
            start_hour=2,
            duration_minutes=180,  # 3 hours only
            is_feasible=True,
            traffic_level="LOW",
        )
        result = self.solver.solve(
            requests=[req],
            windows=[win],
            max_block_duration_hours=6.0,
            target_date=self.target_date,
        )
        self.assertEqual(result.scheduled_task_ids, [])
        self.assertEqual(result.unscheduled_task_ids, ["MR_LONG"])
        self.assertEqual(len(result.blocks), 0)

    def test_03_max_block_duration(self):
        """Test 3: Two tasks (2.5h + 2.5h = 5h) fit window (6h) but exceed max_block_duration (4h) -> Both cannot be placed together."""
        req1 = MaintenanceRequestInput(
            id=1,
            request_id="MR01",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=2.5,
            priority_score=90.0,
        )
        req2 = MaintenanceRequestInput(
            id=2,
            request_id="MR02",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=2.5,
            priority_score=85.0,
        )
        win = MaintenanceWindowInput(
            id=101,
            window_id="MW01",
            section_id="SEC_A",
            start_hour=1,
            duration_minutes=360,  # 6 hours window
            is_feasible=True,
            traffic_level="LOW",
        )
        result = self.solver.solve(
            requests=[req1, req2],
            windows=[win],
            max_block_duration_hours=4.0,  # Max block limit is 4h
            target_date=self.target_date,
        )
        self.assertIn(result.status, ("OPTIMAL", "FEASIBLE"))
        # Only 1 task can fit in the 4h max block limit
        self.assertEqual(len(result.scheduled_task_ids), 1)
        self.assertIn("MR01", result.scheduled_task_ids)  # Higher priority preferred
        self.assertIn("MR02", result.unscheduled_task_ids)

    def test_04_at_most_once(self):
        """Test 4: One task with 3 feasible windows -> Task appears in at most one block."""
        req = MaintenanceRequestInput(
            id=1,
            request_id="MR01",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=2.0,
            priority_score=95.0,
        )
        win1 = MaintenanceWindowInput(id=1, window_id="MW01", section_id="SEC_A", start_hour=1, duration_minutes=180, is_feasible=True)
        win2 = MaintenanceWindowInput(id=2, window_id="MW02", section_id="SEC_A", start_hour=6, duration_minutes=180, is_feasible=True)
        win3 = MaintenanceWindowInput(id=3, window_id="MW03", section_id="SEC_A", start_hour=14, duration_minutes=180, is_feasible=True)

        result = self.solver.solve(
            requests=[req],
            windows=[win1, win2, win3],
            target_date=self.target_date,
        )
        self.assertIn(result.status, ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(result.scheduled_task_ids, ["MR01"])
        self.assertEqual(len(result.blocks), 1)
        self.assertEqual(len(result.blocks[0].tasks), 1)

    def test_05_section_constraint(self):
        """Test 5: Task on SEC_A and window on SEC_B -> Task cannot use that window."""
        req = MaintenanceRequestInput(
            id=1,
            request_id="MR01",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=2.0,
            priority_score=90.0,
        )
        win = MaintenanceWindowInput(
            id=101,
            window_id="MW_B",
            section_id="SEC_B",
            start_hour=2,
            duration_minutes=240,
            is_feasible=True,
        )
        result = self.solver.solve(
            requests=[req],
            windows=[win],
            target_date=self.target_date,
        )
        self.assertEqual(result.scheduled_task_ids, [])
        self.assertEqual(result.unscheduled_task_ids, ["MR01"])
        self.assertEqual(len(result.blocks), 0)

    def test_06_incompatible_departments(self):
        """Test 6: Two incompatible departments on same section/window -> Not bundled together."""
        req_eng = MaintenanceRequestInput(
            id=1,
            request_id="MR_ENG",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=1.5,
            priority_score=90.0,
        )
        req_elec = MaintenanceRequestInput(
            id=2,
            request_id="MR_ELEC",
            section_id="SEC_A",
            department="Electrical",
            duration_hours=1.5,
            priority_score=85.0,
        )
        win = MaintenanceWindowInput(
            id=101,
            window_id="MW01",
            section_id="SEC_A",
            start_hour=2,
            duration_minutes=240,
            is_feasible=True,
            traffic_level="LOW",
        )
        compat = {
            ("Engineering", "Electrical"): "INCOMPATIBLE",
        }
        result = self.solver.solve(
            requests=[req_eng, req_elec],
            windows=[win],
            compatibility_rules=compat,
            target_date=self.target_date,
        )
        self.assertIn(result.status, ("OPTIMAL", "FEASIBLE"))
        # Since only 1 window is available, only 1 of the 2 incompatible tasks can be scheduled
        self.assertEqual(len(result.scheduled_task_ids), 1)
        self.assertIn("MR_ENG", result.scheduled_task_ids)  # Higher priority

    def test_07_compatible_departments(self):
        """Test 7: Two compatible departments on same section/window with enough capacity -> Bundled together."""
        req1 = MaintenanceRequestInput(
            id=1,
            request_id="MR_ENG",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=1.5,
            priority_score=90.0,
        )
        req2 = MaintenanceRequestInput(
            id=2,
            request_id="MR_ST",
            section_id="SEC_A",
            department="S&T",
            duration_hours=1.5,
            priority_score=85.0,
        )
        win = MaintenanceWindowInput(
            id=101,
            window_id="MW01",
            section_id="SEC_A",
            start_hour=2,
            duration_minutes=240,
            is_feasible=True,
            traffic_level="LOW",
        )
        compat = {
            ("Engineering", "S&T"): "COMPATIBLE",
        }
        result = self.solver.solve(
            requests=[req1, req2],
            windows=[win],
            compatibility_rules=compat,
            max_block_duration_hours=4.0,
            target_date=self.target_date,
        )
        self.assertIn(result.status, ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(set(result.scheduled_task_ids), {"MR_ENG", "MR_ST"})
        self.assertEqual(len(result.blocks), 1)
        block = result.blocks[0]
        self.assertEqual(block.task_count, 2)
        self.assertTrue(block.is_bundled)
        self.assertEqual(set(block.departments), {"Engineering", "S&T"})

    def test_08_traffic_preference(self):
        """Test 8: Two otherwise equivalent windows: LOW traffic vs HIGH traffic -> LOW traffic preferred."""
        req = MaintenanceRequestInput(
            id=1,
            request_id="MR01",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=2.0,
            priority_score=80.0,
        )
        win_low = MaintenanceWindowInput(
            id=1,
            window_id="MW_LOW",
            section_id="SEC_A",
            start_hour=1,
            duration_minutes=180,
            expected_train_count=1,
            traffic_level="LOW",
            is_feasible=True,
        )
        win_high = MaintenanceWindowInput(
            id=2,
            window_id="MW_HIGH",
            section_id="SEC_A",
            start_hour=8,
            duration_minutes=180,
            expected_train_count=10,
            traffic_level="HIGH",
            is_feasible=True,
        )
        result = self.solver.solve(
            requests=[req],
            windows=[win_low, win_high],
            target_date=self.target_date,
        )
        self.assertIn(result.status, ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(result.scheduled_task_ids, ["MR01"])
        self.assertEqual(len(result.blocks), 1)
        self.assertEqual(result.blocks[0].window_code, "MW_LOW")

    def test_09_priority_preference(self):
        """Test 9: Two tasks competing for insufficient capacity -> Higher priority task preferred."""
        req_high = MaintenanceRequestInput(
            id=1,
            request_id="MR_HIGH_PRI",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=3.0,
            priority_score=98.0,
            criticality_score=5.0,
        )
        req_low = MaintenanceRequestInput(
            id=2,
            request_id="MR_LOW_PRI",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=3.0,
            priority_score=20.0,
            criticality_score=1.0,
        )
        # Window has only 3 hours capacity (180 mins)
        win = MaintenanceWindowInput(
            id=101,
            window_id="MW01",
            section_id="SEC_A",
            start_hour=2,
            duration_minutes=180,
            is_feasible=True,
        )
        result = self.solver.solve(
            requests=[req_high, req_low],
            windows=[win],
            target_date=self.target_date,
        )
        self.assertIn(result.status, ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(result.scheduled_task_ids, ["MR_HIGH_PRI"])
        self.assertIn("MR_LOW_PRI", result.unscheduled_task_ids)

    def test_10_no_feasible_windows(self):
        """Test 10: No feasible windows -> Valid result returned without crashing."""
        req = MaintenanceRequestInput(
            id=1,
            request_id="MR01",
            section_id="SEC_A",
            department="Engineering",
            duration_hours=2.0,
            priority_score=90.0,
        )
        win_infeasible = MaintenanceWindowInput(
            id=101,
            window_id="MW_INFEASIBLE",
            section_id="SEC_A",
            start_hour=2,
            duration_minutes=240,
            is_feasible=False,
        )
        result = self.solver.solve(
            requests=[req],
            windows=[win_infeasible],
            target_date=self.target_date,
        )
        self.assertEqual(result.status, "INFEASIBLE")
        self.assertEqual(result.scheduled_task_ids, [])
        self.assertEqual(result.unscheduled_task_ids, ["MR01"])
        self.assertEqual(len(result.blocks), 0)


if __name__ == "__main__":
    unittest.main()
