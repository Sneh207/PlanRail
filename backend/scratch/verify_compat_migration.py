"""
Verification script: confirm compatibility column is VARCHAR(50)
and all tables remain intact with zero application data.
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

DATABASE_URL = os.environ["DATABASE_URL"]

from sqlalchemy import create_engine, text

engine = create_engine(DATABASE_URL)

EXPECTED_TABLES = [
    "stations", "railway_sections", "trains", "train_schedules",
    "assets", "maintenance_requests", "maintenance_history",
    "crew_availability", "maintenance_compatibility",
    "traffic_windows", "maintenance_windows",
    "users", "optimization_runs", "optimized_blocks", "block_tasks",
    "simulation_runs", "train_movements",
]

with engine.connect() as conn:
    # 1. Check compatibility column type
    row = conn.execute(text("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'maintenance_compatibility'
          AND column_name = 'compatibility'
    """)).fetchone()

    print("=== compatibility column ===")
    if row:
        print(f"  column_name : {row[0]}")
        print(f"  data_type   : {row[1]}")
        print(f"  max_length  : {row[2]}")
        print(f"  is_nullable : {row[3]}")
        assert row[1] == 'character varying', f"FAIL: expected VARCHAR, got {row[1]}"
        assert row[2] == 50, f"FAIL: expected length 50, got {row[2]}"
        print("  PASS -- column is VARCHAR(50)")
    else:
        print("  FAIL -- column not found")
        sys.exit(1)

    # 2. Confirm unique constraint still exists
    uc = conn.execute(text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'maintenance_compatibility'
          AND constraint_type = 'UNIQUE'
          AND constraint_name = 'uq_department_pair'
    """)).fetchone()
    print("\n=== unique constraint ===")
    if uc:
        print("  PASS -- uq_department_pair constraint present")
    else:
        print("  FAIL -- uq_department_pair not found")
        sys.exit(1)

    # 3. Check all expected tables exist
    print("\n=== table existence ===")
    existing = {r[0] for r in conn.execute(text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
    """)).fetchall()}
    missing = [t for t in EXPECTED_TABLES if t not in existing]
    if missing:
        print(f"  FAIL -- missing tables: {missing}")
        sys.exit(1)
    print(f"  PASS -- all {len(EXPECTED_TABLES)} expected tables present")

    # 4. Row counts -- all dataset tables must be 0
    print("\n=== application data (must all be 0) ===")
    dataset_tables = [
        "stations", "railway_sections", "trains", "train_schedules",
        "assets", "maintenance_requests", "maintenance_history",
        "crew_availability", "maintenance_compatibility",
        "traffic_windows", "maintenance_windows",
    ]
    all_zero = True
    for tbl in dataset_tables:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
        status = "OK" if count == 0 else "NON-ZERO"
        print(f"  [{status}]  {tbl}: {count} rows")
        if count != 0:
            all_zero = False

    if all_zero:
        print("\nALL CHECKS PASSED -- migration d71c348de844 verified successfully.")
    else:
        print("\nWARNING: Some tables have unexpected data -- review before proceeding.")
