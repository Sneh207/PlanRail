from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.optimization_service import OptimizationService
from app.services.simulation_service import SimulationService
from app.services.ai_service import AIService
from app.schemas import (
    OptimizationGenerateRequest,
    OptimizationGenerateResponse,
    AIPredictRequest,
    AIPredictResponse,
    AIInsightsResponse,
    SimulationRunRequest,
    SimulationRunResponse,
    ErrorResponse,
)

router = APIRouter()

@router.post(
    "/optimization/generate",
    response_model=OptimizationGenerateResponse,
    summary="Generate Optimization Plan",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def generate_optimization(
    request: OptimizationGenerateRequest,
    db: Session = Depends(get_db),
):
    return OptimizationService.generate_optimization_plan(db, request)

@router.post(
    "/ai/predict",
    response_model=AIPredictResponse,
    summary="AI Priority and Risk Prediction",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def ai_predict(
    request: AIPredictRequest,
    db: Session = Depends(get_db),
):
    return AIService.predict_request(db, request.request_id)

@router.get(
    "/ai/insights",
    response_model=AIInsightsResponse,
    summary="Corridor AI Aggregated Insights",
    responses={
        500: {"model": ErrorResponse},
    }
)
def get_ai_insights(
    db: Session = Depends(get_db),
):
    return AIService.get_corridor_insights(db)

@router.post(
    "/simulation/run",
    response_model=SimulationRunResponse,
    summary="Run What-If Simulation",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def run_simulation(
    request: SimulationRunRequest,
    db: Session = Depends(get_db),
):
    return SimulationService.run_simulation(db, request)
