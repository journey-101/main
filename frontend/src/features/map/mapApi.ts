export interface Place {
  id: string | number;
  name: string;
  address: string;
  lat: number;
  lng: number;
}

// 임의의 고정 사용자 현위치 데이터
const CURRENT_LOCATION = { name: "인천지방법원부천지원", lat: 37.4938, lng: 126.7513 };

export type TripAttemptStatus = "started" | "completed" | "aborted";

export interface CurrentAttempt {
  id: string;
  status: TripAttemptStatus;
  feedback_text: string | null;
}

export interface ApiResponse<T> {
  success: true;
  data: T;
}

class ApiError extends Error {
  constructor(public readonly status: number) {
    super(`Trips API request failed with status ${status}`);
    this.name = "ApiError";
  }
}

export interface TripListItem {
  id: string;
  user_id: string;
  title: string;
  current_attempt: CurrentAttempt;
}

export interface TripDetail {
  id: string;
  user_id: string;
  title: string;
  attempts: TripAttempt[];
}

export interface CreateTripRequest {
  user_id: string;
  title: string;
}

export interface UpdateTripRequest {
  title: string;
}

export interface CreateAttemptRequest {
  status?: TripAttemptStatus;
}

export interface UpdateAttemptRequest {
  status?: TripAttemptStatus;
  feedback_text?: string;
}

export interface UpdateFeedbackRequest {
  feedback_text: string;
}

export interface TripAttempt {
  id: string;
  trip_id: string;
  status: TripAttemptStatus;
  feedback_text: string | null;
  created_at: string;
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

const getTripsUrl = (path = ""): string => {
  return `${getApiBaseUrl()}/api/v1/trips${path}`;
};

const requestJson = async <TResponse>(
  path: string,
  options: RequestInit = {},
): Promise<ApiResponse<TResponse>> => {
  const response = await fetch(getTripsUrl(path), {
    ...options,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return (await response.json()) as ApiResponse<TResponse>;
};

export const getCurrentLocation = () => {
  return CURRENT_LOCATION;
};

const normalizePlace = (raw: any): Place => ({
  id: raw.id ?? raw.provider_place_id ?? raw.place_id ?? Date.now(),
  name: raw.name ?? raw.place_name ?? "이름 없음",
  address: raw.address ?? raw.road_address ?? raw.addr ?? "",
  lat: Number(raw.lat ?? raw.latitude ?? 0),
  lng: Number(raw.lng ?? raw.longitude ?? 0),
});

const normalizePlaceResponse = (payload: any): Place[] => {
  if (Array.isArray(payload)) {
    return payload.map(normalizePlace);
  }

  const items =
    payload?.data?.items ??
    payload?.items ??
    payload?.data?.results ??
    [];

  if (Array.isArray(items)) {
    return items.map(normalizePlace);
  }

  return [];
};

export const fetchPlacesFromApi = async (): Promise<Place[]> => {
  const baseUrl = getApiBaseUrl();
  const candidatePaths = ["/api/v1/places/search", "/api/v1/places"];

  for (const path of candidatePaths) {
    try {
      const url = new URL(path, `${baseUrl}/`);
      url.searchParams.set("limit", "20");

      const response = await fetch(url.toString(), {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        continue;
      }

      const payload = await response.json();
      return normalizePlaceResponse(payload);
    } catch (error) {
      console.warn("Place API request failed", error);
    }
  }

  throw new Error("Place API request failed");
};

const getTestUserId = (): string => {
  return import.meta.env.VITE_TEST_USER_ID as string;
};

export const getTripsApi = async (): Promise<ApiResponse<TripListItem[]>> => {
  const userId = getTestUserId();

  const url = `/api/v1/trips?user_id=${encodeURIComponent(userId)}`;

  const response = await fetch(`${getApiBaseUrl()}${url}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return (await response.json()) as ApiResponse<TripListItem[]>;
};

export const createTripApi = async (
  tripData: CreateTripRequest,
): Promise<ApiResponse<TripListItem>> => {
  return requestJson<TripListItem>("", {
    method: "POST",
    body: JSON.stringify(tripData),
  });
};

export const getTripByIdApi = async (
  tripId: string,
): Promise<ApiResponse<TripDetail>> => {
  return requestJson<TripDetail>(`/${tripId}`, {
    method: "GET",
  });
};

export const updateTripApi = async (
  tripId: string,
  tripData: UpdateTripRequest,
): Promise<ApiResponse<TripListItem>> => {
  return requestJson<TripListItem>(`/${tripId}`, {
    method: "PATCH",
    body: JSON.stringify(tripData),
  });
};

export const createTripAttemptApi = async (
  tripId: string,
  attemptData: CreateAttemptRequest = {},
): Promise<ApiResponse<TripAttempt>> => {
  return requestJson<TripAttempt>(`/${tripId}/attempts`, {
    method: "POST",
    body: JSON.stringify(attemptData),
  });
};

export const updateTripAttemptApi = async (
  tripId: string,
  attemptId: string,
  attemptData: UpdateAttemptRequest,
): Promise<ApiResponse<TripAttempt>> => {
  return requestJson<TripAttempt>(`/${tripId}/attempts/${attemptId}`, {
    method: "PATCH",
    body: JSON.stringify(attemptData),
  });
};

export const updateTripFeedbackApi = async (
  tripId: string,
  attemptId: string,
  feedbackData: UpdateFeedbackRequest,
): Promise<ApiResponse<TripAttempt>> => {
  return requestJson<TripAttempt>(
    `/${tripId}/attempts/${attemptId}/feedback`,
    {
      method: "PATCH",
      body: JSON.stringify(feedbackData),
    },
  );
};
