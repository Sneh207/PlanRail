from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    OptimizationGenerateRequest,
    AIPredictRequest,
    AIPredictResponse,
    SimulationRunRequest,
    ErrorResponse
)

router = APIRouter()

@router.post(
    "/optimization/generate",
    summary="Generate Optimization Plan",
    responses={
        501: {"model": ErrorResponse}
    }
)
def generate_optimization(request: OptimizationGenerateRequest):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"code": "NOT_IMPLEMENTED", "message": "Optimization engine is not yet connected."}
    )

@router.post(
    "/ai/predict",
    response_model=AIPredictResponse,
    summary="AI Priority and Risk Prediction",
    responses={
        501: {"model": ErrorResponse}
    }
)
def ai_predict(request: AIPredictRequest):
    # Deterministic fallback interface
    return AIPredictResponse(
        request_id=request.request_id,
        priority_score=85.0,
        risk_score=75.0,
        risk_category="HIGH"
    )

@router.post(
    "/simulation/run",
    summary="Run What-If Simulation",
    responses={
        501: {"model": ErrorResponse}
    }
)
def run_simulation(request: SimulationRunRequest):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"code": "NOT_IMPLEMENTED", "message": "Simulation engine is not yet connected."}
    )
