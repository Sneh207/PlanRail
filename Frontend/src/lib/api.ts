import axios, { AxiosError } from "axios";
import type {
  AIPredictRequest,
  AIPredictResponse,
  AIInsightsResponse,
  AssetResponse,
  DashboardResponse,
  MaintenanceRequestDetailResponse,
  MaintenanceRequestResponse,
  OptimizationGenerateRequest,
  OptimizationGenerateResponse,
  OptimizedBlockResponse,
  PaginatedResponse,
  SectionResponse,
  SimulationRunRequest,
  SimulationRunResponse,
  StationResponse,
  TrainResponse,
  TrainScheduleResponse,
  FreightTrainMovementResponse,
} from "./types";

const RAW_BASE_URL = import.meta.env["VITE_API_BASE_URL"];
const BASE_URL = typeof RAW_BASE_URL === "string" ? RAW_BASE_URL.replace(/\/+$/, "") : "";

export const apiClient = axios.create({
  baseURL: BASE_URL || "http://localhost:8000",
  headers: { Accept: "application/json" },
  timeout: 15000,
});

export type JsonRecord = Record<string, unknown>;

export function apiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (data && typeof data === "object" && "message" in data && typeof data.message === "string") {
      return data.message;
    }
    if (data && typeof data === "object" && "detail" in data) {
      if (typeof data.detail === "string") return data.detail;
      if (typeof data.detail === "object" && data.detail !== null && "message" in data.detail) {
        return String((data.detail as { message: unknown }).message);
      }
    }
    const status = error.response?.status;
    if (status) return `${fallback} (HTTP ${status}).`;
    if (error.code === "ECONNABORTED") return `${fallback}: Connection timed out.`;
    if (error.request) return `${fallback}: Cannot reach backend at ${BASE_URL || "http://localhost:8000"}. Please check server status.`;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return fallback;
}

async function getJson<T>(path: string, params?: Record<string, unknown>): Promise<T> {
  try {
    const response = await apiClient.get<T>(path, { params });
    return response.data;
  } catch (error) {
    throw error;
  }
}

async function postJson<T>(
  path: string,
  body?: unknown,
): Promise<{ status: number; data: T }> {
  try {
    const response = await apiClient.post<T>(path, body);
    return { status: response.status, data: response.data };
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return { status: error.response.status, data: error.response.data as T };
    }
    throw error;
  }
}

export const api = {
  health: () => getJson<{ status: string }>("/api/v1/health"),
  healthDb: () =>
    getJson<{ status: string; database: string; postgis: boolean }>("/api/v1/health/db"),
  dashboard: () => getJson<DashboardResponse>("/api/v1/dashboard"),
  sections: (params?: { page?: number; page_size?: number }) =>
    getJson<PaginatedResponse<SectionResponse>>("/api/v1/sections", params),
  section: (sectionId: string) =>
    getJson<SectionResponse>(`/api/v1/sections/${encodeURIComponent(sectionId)}`),
  stations: (params?: { page?: number; page_size?: number; search?: string }) =>
    getJson<PaginatedResponse<StationResponse>>("/api/v1/stations", params),
  station: (stationId: string) =>
    getJson<StationResponse>(`/api/v1/stations/${encodeURIComponent(stationId)}`),
  assets: (params?: {
    section_id?: string;
    department?: string;
    asset_type?: string;
    criticality?: string;
    page?: number;
    page_size?: number;
  }) => getJson<PaginatedResponse<AssetResponse>>("/api/v1/assets", params),
  asset: (assetId: string) =>
    getJson<AssetResponse>(`/api/v1/assets/${encodeURIComponent(assetId)}`),
  maintenance: (params?: {
    status?: string;
    department?: string;
    section_id?: string;
    asset_id?: string;
    criticality?: string;
    severity?: string;
    page?: number;
    page_size?: number;
  }) => getJson<PaginatedResponse<MaintenanceRequestResponse>>("/api/v1/maintenance", params),
  maintenanceRequest: (requestId: string) =>
    getJson<MaintenanceRequestDetailResponse>(
      `/api/v1/maintenance/${encodeURIComponent(requestId)}`,
    ),
  trains: (params?: { train_type?: string; page?: number; page_size?: number }) =>
    getJson<PaginatedResponse<TrainResponse>>("/api/v1/trains", params),
  train: (trainNumber: string) =>
    getJson<TrainResponse>(`/api/v1/trains/${encodeURIComponent(trainNumber)}`),
  trainSchedule: (trainNumber: string) =>
    getJson<TrainScheduleResponse[]>(`/api/v1/trains/${encodeURIComponent(trainNumber)}/schedule`),
  freightTrains: (params?: {
    movement_date?: string;
    traffic_priority?: string;
    commodity?: string;
    origin_station_code?: string;
    destination_station_code?: string;
    page?: number;
    page_size?: number;
  }) => getJson<PaginatedResponse<FreightTrainMovementResponse>>("/api/v1/freight-trains", params),
  freightTrain: (freightTrainId: string) =>
    getJson<FreightTrainMovementResponse>(`/api/v1/freight-trains/${encodeURIComponent(freightTrainId)}`),
  blocks: (params?: { page?: number; page_size?: number }) =>
    getJson<PaginatedResponse<OptimizedBlockResponse>>("/api/v1/blocks", params),
  block: (blockId: string) =>
    getJson<OptimizedBlockResponse>(`/api/v1/blocks/${encodeURIComponent(blockId)}`),
  generateOptimization: (body: OptimizationGenerateRequest) =>
    postJson<OptimizationGenerateResponse>("/api/v1/optimization/generate", body),
  predict: (body: AIPredictRequest) =>
    postJson<AIPredictResponse>("/api/v1/ai/predict", body),
  aiInsights: () => getJson<AIInsightsResponse>("/api/v1/ai/insights"),
  runSimulation: (body: SimulationRunRequest) =>
    postJson<SimulationRunResponse>("/api/v1/simulation/run", body),
};

export function asRecords(value: unknown): JsonRecord[] {
  if (Array.isArray(value)) return value.filter(isRecord);
  if (!isRecord(value)) return [];

  for (const key of [
    "data",
    "items",
    "results",
    "sections",
    "stations",
    "assets",
    "maintenance",
    "requests",
    "trains",
    "schedule",
    "stops",
    "blocks",
    "tasks",
  ]) {
    const nested = value[key];
    if (Array.isArray(nested)) return nested.filter(isRecord);
  }

  return [];
}

export function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function readValue(record: JsonRecord | null | undefined, keys: readonly string[]): unknown {
  if (!record) return undefined;
  for (const key of keys) {
    if (key in record) return record[key];
  }
  return undefined;
}

export function readNumber(
  record: JsonRecord | null | undefined,
  keys: readonly string[],
): number | null {
  const value = readValue(record, keys);
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "" && Number.isFinite(Number(value))) {
    return Number(value);
  }
  return null;
}

export function readText(
  record: JsonRecord | null | undefined,
  keys: readonly string[],
): string | null {
  const value = readValue(record, keys);
  return typeof value === "string" && value.trim() !== "" ? value : null;
}
