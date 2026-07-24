export interface Preferences {
  user_id: string;
  preferred_categories: string[];
  avoided_categories: string[];
  prefers_quiet: boolean;
  max_walk_minutes: number;
  is_first_time_traveler: boolean;
}

export type UpdatePreferencesRequest = Preferences;

export interface RecommendationTarget {
  type: "place" | "trip";
  region_code?: string;
  trip_id?: string;
}

export interface RecommendationRequest {
  user_id: string;
  method: "preference_mock";
  target: RecommendationTarget;
  limit: number;
}

export interface RecommendationItem {
  place_id: string | number;
  place_name: string;
  category: string;
  score: number;
  rank: number;
  reasons: string[];
}

export interface RecommendationResponse {
  method: string;
  target: RecommendationTarget;
  fallback?: {
    used: boolean;
    reason?: string;
    fallback_target?: RecommendationTarget;
  };
  items: RecommendationItem[];
}

interface ApiResponse<T> {
  success: true;
  data: T;
}

class PreferencesApiError extends Error {
  constructor(public readonly status: number) {
    super(`Preferences API request failed with status ${status}`);
    this.name = "PreferencesApiError";
  }
}

const getApiBaseUrl = (): string => {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as
    | string
    | undefined;

  if (configuredBaseUrl && configuredBaseUrl.trim()) {
    return configuredBaseUrl.replace(/\/$/, "");
  }

  return "http://localhost:8000";
};

const requestJson = async <TResponse>(
  path: string,
  options: RequestInit = {},
): Promise<ApiResponse<TResponse>> => {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new PreferencesApiError(response.status);
  }

  return (await response.json()) as ApiResponse<TResponse>;
};

export const getPreferencesApi = async (
  userId: string,
): Promise<ApiResponse<Preferences>> => {
  const query = `?user_id=${encodeURIComponent(userId)}`;

  return requestJson<Preferences>(`/api/v1/me/preferences${query}`, {
    method: "GET",
  });
};

export const updatePreferencesApi = async (
  preferences: UpdatePreferencesRequest,
): Promise<ApiResponse<Preferences>> => {
  return requestJson<Preferences>("/api/v1/me/preferences", {
    method: "PUT",
    body: JSON.stringify(preferences),
  });
};

// Recommendation API는 현재 실제 호출하지 않는다.
// 향후 아래 요청 타입과 응답 타입을 사용해 Service 내부에 연결한다.
export type RecommendationApiResponse = ApiResponse<RecommendationResponse>;