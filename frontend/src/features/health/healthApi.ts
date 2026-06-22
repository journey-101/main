import { getJson } from "../../shared/api/client";
import type { DatabaseHealthResponse, ServiceHealthResponse } from "./types";

export function fetchBackendHealth(): Promise<ServiceHealthResponse> {
  return getJson<ServiceHealthResponse>("/api/v1/health");
}

export function fetchDatabaseHealth(): Promise<DatabaseHealthResponse> {
  return getJson<DatabaseHealthResponse>("/api/v1/health/db");
}
