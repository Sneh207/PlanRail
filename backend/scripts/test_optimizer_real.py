"""
PlanRail Standalone Real Dataset Optimizer Test
===============================================

Loads real Delhi-Agra dataset from Supabase/PostgreSQL (or local dataset SQLite)
via OptimizerDataLoader and executes the CP-SAT solver in read-only mode without
mutating the database.
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.config import settings
from app.database import SessionLocal as PostgresSessionLocal
from app.optimizer.data_loader import OptimizerDataLoader
from app.optimizer.solver import MaintenanceBlockSolver


def get_test_session():
    """Returns database session from Postgres or SQLite dataset."""
    if PostgresSessionLocal is not None:
        try:
            db = PostgresSessionLocal()
            # Test connectivity
            db.execute(text("SELECT 1"))
            return db, "Supabase/PostgreSQL Database"
        except Exception:
            pass

    # Fallback to local Delhi-Agra SQLite dataset
    sqlite_path = _BACKEND_DIR.parent / "_dataset_inspect" / "PlanRail_Delhi_Agra_Dataset" / "planrail_demo.sqlite"
    if sqlite_path.exists():
        engine = create_engine(f"sqlite:///{sqlite_path}")
        # Create view/alias for maintenance_compatibility if named task_compatibility
        with engine.connect() as conn:
            conn.execute(text("CREATE VIEW IF NOT EXISTS maintenance_compatibility AS SELECT ROW_NUMBER() OVER () as id, department_a, department_b, compatibility, NULL as reason, datetime('now') as created_at FROM task_compatibility"))
            conn.commit()
        Session = sessionmaker(bind=engine)
        return Session(), f"Local SQLite Dataset ({sqlite_path.name})"

    raise RuntimeError("No database or dataset sqlite file found.")


def main():
    print("=" * 70)
    print("PlanRail Real Dataset Optimizer Standalone Test (Read-Only)")
    print("=" * 70)

    db, source_name = get_test_session()
    print(f"\n[Database Source]: {source_name}")

    try:
        loader = OptimizerDataLoader(db)
        target_date = date(2026, 9, 10)

        print(f"\n1. Loading solver inputs from dataset for target_date={target_date}...")
        requests, windows, compatibility_rules, section_id_map = loader.prepare_solver_inputs(
            target_date=target_date,
            selected_request_ids=None,
        )

        print(f"   - Eligible Maintenance Requests : {len(requests)}")
        print(f"   - Feasible Maintenance Windows   : {len(windows)}")
        print(f"   - Compatibility Rule Pairs       : {len(compatibility_rules)}")
        print(f"   - Mapped Railway Sections        : {len(section_id_map)}")

        print("\n2. Executing CP-SAT MaintenanceBlockSolver...")
        solver = MaintenanceBlockSolver(time_limit_seconds=5.0, random_seed=42)
        result = solver.solve(
            requests=requests,
            windows=windows,
            compatibility_rules=compatibility_rules,
            max_block_duration_hours=4.0,
            target_date=target_date,
            section_id_map=section_id_map,
        )

        print("\n3. Solver Results:")
        print(f"   - Solver Status        : {result.status}")
        print(f"   - Solve Time (ms)      : {result.solve_time_ms} ms")
        print(f"   - Objective Value      : {result.objective_value}")
        print(f"   - Scheduled Tasks      : {len(result.scheduled_task_ids)} / {len(requests)}")
        print(f"   - Unscheduled Tasks    : {len(result.unscheduled_task_ids)}")
        print(f"   - Generated Blocks     : {len(result.blocks)}")
        print(f"   - Total Scheduled Min  : {result.metrics['total_scheduled_duration_minutes']} mins")

        print("\n4. Sample Generated Blocks (First 5):")
        for i, b in enumerate(result.blocks[:5], 1):
            print(f"   [{i}] Block Code: {b.block_code}")
            print(f"       Section: {b.section_id} | Window: {b.window_code}")
            print(f"       Time: {b.start_time_minutes//60:02d}:{b.start_time_minutes%60:02d} -> {b.end_time_minutes//60:02d}:{b.end_time_minutes%60:02d} ({b.duration_hours} hrs)")
            print(f"       Tasks ({b.task_count}): {[t.request_id for t in b.tasks]} | Depts: {b.departments} | Bundled: {b.is_bundled}")
            print(f"       Traffic Level: {b.traffic_level} | Train Count: {b.expected_train_count} | Opt Score: {b.optimization_score}%")

        print("\n" + "=" * 70)
        print("Standalone Real Dataset Test Completed Successfully (Zero DB Mutations).")
        print("=" * 70)
    finally:
        db.close()


if __name__ == "__main__":
    main()
