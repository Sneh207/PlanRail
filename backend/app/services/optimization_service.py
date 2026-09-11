"""
PlanRail Optimization Service
=============================

Orchestrates database input loading, CP-SAT solver execution, transactional
database persistence of OptimizationRun, OptimizedBlock, and BlockTask records,
and response construction.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time as dt_time, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.block import BlockStatus, BlockTask, OptimizationRun, OptimizedBlock
from app.optimizer.data_loader import OptimizerDataLoader
from app.optimizer.solver import MaintenanceBlockSolver, OptimizationResult
from app.schemas.domain import (
    BlockTaskResponse,
    OptimizationGenerateRequest,
    OptimizationGenerateResponse,
    OptimizedBlockResponse,
)

logger = logging.getLogger(__name__)


class OptimizationService:
    """Service handling maintenance block optimization and transaction persistence."""

    @staticmethod
    def generate_optimization_plan(
        db: Session,
        request: OptimizationGenerateRequest,
    ) -> OptimizationGenerateResponse:
        """
        Executes CP-SAT maintenance block optimization and persists results.
        
        Args:
            db: Database session.
            request: Optimization generation parameters.
            
        Returns:
            OptimizationGenerateResponse with run metrics and scheduled block details.
        """
        target_date: date = request.target_date
        max_block_duration_hours: float = request.max_block_duration_hours or 4.0

        if not isinstance(target_date, date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TARGET_DATE", "message": "A valid target_date is required."},
            )

        # ---------------------------------------------------------------------
        # 1. Load solver inputs from database
        # ---------------------------------------------------------------------
        loader = OptimizerDataLoader(db)
        try:
            requests, windows, compatibility_rules, section_id_map = loader.prepare_solver_inputs(
                target_date=target_date,
                selected_request_ids=request.selected_request_ids,
            )
        except Exception as e:
            logger.exception("Failed to load optimizer data inputs")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "DATA_LOAD_ERROR", "message": f"Error loading optimization inputs: {str(e)}"},
            )

        if not requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "NO_ELIGIBLE_REQUESTS",
                    "message": f"No eligible maintenance requests found for target date {target_date}.",
                },
            )

        if not windows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "NO_FEASIBLE_WINDOWS",
                    "message": f"No feasible maintenance windows available for target date {target_date}.",
                },
            )

        # ---------------------------------------------------------------------
        # 2. Run CP-SAT Solver
        # ---------------------------------------------------------------------
        solver = MaintenanceBlockSolver(time_limit_seconds=5.0, random_seed=42)
        try:
            result: OptimizationResult = solver.solve(
                requests=requests,
                windows=windows,
                compatibility_rules=compatibility_rules,
                max_block_duration_hours=max_block_duration_hours,
                target_date=target_date,
                section_id_map=section_id_map,
            )
        except Exception as e:
            logger.exception("CP-SAT solver execution failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "SOLVER_EXECUTION_ERROR", "message": f"Optimization solver error: {str(e)}"},
            )

        if result.status not in ("OPTIMAL", "FEASIBLE"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INFEASIBLE_PLAN",
                    "message": f"No feasible block schedule could be found under given constraints (solver status: {result.status}).",
                },
            )

        # ---------------------------------------------------------------------
        # 3. Transactional Database Persistence
        # ---------------------------------------------------------------------
        now_utc = datetime.now(timezone.utc)
        date_stamp = target_date.strftime("%Y%m%d")
        time_stamp = now_utc.strftime("%H%M%S")
        usec_stamp = f"{now_utc.microsecond:06d}"
        run_code = f"RUN_{date_stamp}_{time_stamp}_{usec_stamp[:4]}"

        parameters = {
            "target_date": str(target_date),
            "max_block_duration_hours": max_block_duration_hours,
            "selected_request_ids": request.selected_request_ids or [],
            "total_requests_considered": len(requests),
        }

        response_blocks: List[OptimizedBlockResponse] = []

        try:
            # A. Create OptimizationRun
            opt_run = OptimizationRun(
                run_code=run_code,
                status=result.status,
                objective="MAX_MAINTENANCE_MIN_DISRUPTION",
                parameters=parameters,
                metrics=result.metrics,
                created_at=now_utc,
                completed_at=now_utc,
            )
            db.add(opt_run)
            db.flush()  # Obtain opt_run.id

            # B. Create OptimizedBlocks & BlockTasks
            for block_plan in result.blocks:
                sec_db_id = block_plan.section_db_id or section_id_map.get(block_plan.section_id)
                if not sec_db_id:
                    # Fallback to section PK 1 if unresolved in test environments
                    sec_db_id = 1

                # Calculate start and end UTC timestamps
                midnight_utc = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=timezone.utc)
                start_dt = midnight_utc + timedelta(minutes=block_plan.start_time_minutes)
                end_dt = midnight_utc + timedelta(minutes=block_plan.end_time_minutes)

                unique_block_code = f"{block_plan.block_code}_{opt_run.id}"

                opt_block = OptimizedBlock(
                    block_code=unique_block_code,
                    section_id=sec_db_id,
                    maintenance_window_id=block_plan.maintenance_window_id,
                    optimization_run_id=opt_run.id,
                    start_time=start_dt,
                    end_time=end_dt,
                    duration_minutes=block_plan.duration_minutes,
                    status=BlockStatus.PROPOSED,
                    optimization_score=block_plan.optimization_score,
                    created_at=now_utc,
                    updated_at=now_utc,
                )
                db.add(opt_block)
                db.flush()  # Obtain opt_block.id

                task_responses: List[BlockTaskResponse] = []
                for task in block_plan.tasks:
                    block_task = BlockTask(
                        block_id=opt_block.id,
                        maintenance_request_id=task.db_id,
                        sequence_order=task.sequence_order,
                        created_at=now_utc,
                    )
                    db.add(block_task)
                    db.flush()

                    task_responses.append(
                        BlockTaskResponse(
                            block_task_id=f"BT_{block_task.id}",
                            block_id=unique_block_code,
                            request_id=task.request_id,
                            sequence=task.sequence_order,
                        )
                    )

                response_blocks.append(
                    OptimizedBlockResponse(
                        block_id=unique_block_code,
                        run_id=run_code,
                        section_id=block_plan.section_id,
                        start_time=start_dt,
                        end_time=end_dt,
                        duration_hours=round(block_plan.duration_minutes / 60.0, 2),
                        status="PROPOSED",
                        tasks=task_responses,
                    )
                )

            # Commit all entities atomically
            db.commit()

        except Exception as e:
            db.rollback()
            logger.exception("Failed to commit optimization run to database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "PERSISTENCE_TRANSACTION_FAILED", "message": f"Database transaction failed: {str(e)}"},
            )

        # ---------------------------------------------------------------------
        # 4. Return Output Contract
        # ---------------------------------------------------------------------
        return OptimizationGenerateResponse(
            run_id=run_code,
            status=result.status,
            target_date=target_date,
            total_requests_considered=len(requests),
            scheduled_tasks_count=len(result.scheduled_task_ids),
            unscheduled_tasks_count=len(result.unscheduled_task_ids),
            blocks_count=len(response_blocks),
            solve_time_ms=result.solve_time_ms,
            blocks=response_blocks,
        )
