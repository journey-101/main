export interface Place {
  id: number;
  name: string;
  address: string;
  lat: number;
  lng: number;
}

// 임의의 고정 사용자 현위치 데이터
const CURRENT_LOCATION = { name: "서울시청", lat: 37.5665, lng: 126.9780 };

// trips attempt type 관리 및 patch용 선언
export type TripAttemptStatus = 'started' | 'completed' | 'aborted';
const isValidAttemptStatus = (status: string): status is TripAttemptStatus => {
  return status === 'started' || status === 'completed' || status === 'aborted';
};

// 1. 여정 생성 요청 데이터 타입 (POST body)
export interface CreateTripRequest {
  title: string;
  origin_region_code: string;
  destination_region_code: string;
}

// 2. 여정 응답 데이터 타입 (GET / PATCH / POST 응답)
export interface TripResponse extends CreateTripRequest {
  id: string;
  status: string;
  feedback_text: string[];
  attemptId?: string;
  attemptStatus?: TripAttemptStatus;
}

export interface TripAttemptResponse {
  id: string;
  tripId: string;
  status: TripAttemptStatus;
}

// 가상 UUID 생성 함수
const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

const getApiBaseUrl = (): string => {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (configuredBaseUrl && configuredBaseUrl.trim()) {
    return configuredBaseUrl.replace(/\/$/, '');
  }
  return 'http://localhost:8000';
};

const normalizePlace = (raw: any): Place => ({
  id: Number(raw.id ?? raw.provider_place_id ?? raw.place_id ?? Date.now()),
  name: raw.name ?? '이름 없음',
  address: raw.address ?? '',
  lat: Number(raw.lat ?? 0),
  lng: Number(raw.lng ?? 0),
});

const normalizePlaceResponse = (payload: any): Place[] => {
  if (Array.isArray(payload)) {
    return payload.map(normalizePlace);
  }
  if (payload && Array.isArray(payload.items)) {
    return payload.items.map(normalizePlace);
  }
  if (payload && Array.isArray(payload.data)) {
    return payload.data.map(normalizePlace);
  }
  return [];
};

const readStorage = <T>(key: string, fallback: T): T => {
  if (typeof window === 'undefined') {
    return fallback;
  }

  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
};

const writeStorage = <T>(key: string, value: T): void => {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(key, JSON.stringify(value));
};

// 기기 환경 또는 고정된 출발지(현위치) 데이터를 가져오는 함수
export const getCurrentLocation = () => {
  return CURRENT_LOCATION;
};


// 실제 백엔드 place API 호출
export const fetchPlacesFromApi = async (): Promise<Place[]> => {
  const baseUrl = getApiBaseUrl();
  const candidatePaths = ['/api/v1/places/search', '/api/v1/places'];

  for (const path of candidatePaths) {
    try {
      const url = new URL(path, `${baseUrl}/`);
      url.searchParams.set('limit', '20');

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        continue;
      }

      const payload = await response.json();
      const places = normalizePlaceResponse(payload);

      if (places.length > 0) {
        return places;
      }

      return [];
    } catch (error) {
      console.warn(`500 {"detail": "Unknown place data error"}`, error);
    }
  }

  throw new Error('백엔드 place API 호출에 실패했습니다.');
};

// trips persistence (frontend storage)
const TRIP_STORAGE_KEY = 'trip-data-storage';
const ATTEMPT_STORAGE_KEY = 'trip-attempt-storage';

// [POST] 여정 생성
export const createTripApi = async (tripData: CreateTripRequest): Promise<{ success: boolean; data: TripResponse }> => {
  console.log('[API POST] /trips 요청 데이터:', tripData);

  const generatedId = generateUUID();
  const attemptId = generateUUID();

  const newTrip: TripResponse = {
    ...tripData,
    id: generatedId,
    status: 'started',
    feedback_text: [],
    attemptId,
    attemptStatus: 'started',
  };

  const trips = readStorage<Record<string, TripResponse>>(TRIP_STORAGE_KEY, {});
  const attempts = readStorage<Record<string, TripAttemptResponse>>(ATTEMPT_STORAGE_KEY, {});

  trips[generatedId] = newTrip;
  attempts[generatedId] = {
    id: attemptId,
    tripId: generatedId,
    status: 'started',
  };

  writeStorage(TRIP_STORAGE_KEY, trips);
  writeStorage(ATTEMPT_STORAGE_KEY, attempts);

  console.log(`[API POST] 여정 생성 완료 - 경로: /trips/${generatedId}`);
  return { success: true, data: newTrip };
};

// [GET] 여정 단건 조회
export const getTripByIdApi = async (trips_id: string): Promise<{ success: boolean; data: TripResponse | null }> => {
  console.log(`[API GET] /trips/${trips_id} 호출`);

  const trips = readStorage<Record<string, TripResponse>>(TRIP_STORAGE_KEY, {});
  const trip = trips[trips_id];

  if (!trip) {
    console.warn(`[API GET] /trips/${trips_id} 데이터를 찾을 수 없습니다.`);
    return { success: false, data: null };
  }

  const attempts = readStorage<Record<string, TripAttemptResponse>>(ATTEMPT_STORAGE_KEY, {});
  const attempt = attempts[trips_id];

  const tripWithAttempt = {
    ...trip,
    attemptId: attempt?.id ?? trip.attemptId,
    attemptStatus: attempt?.status ?? trip.attemptStatus ?? 'started',
  };

  console.log(`[API GET] /trips/${trips_id} 조회 성공:`, tripWithAttempt);
  return { success: true, data: tripWithAttempt };
};

// [PATCH] 여정 수정 (후기 태그 수집용)
export const updateTripApi = async (
  trips_id: string,
  updatedFields: Partial<TripResponse>
): Promise<{ success: boolean; data: TripResponse | null }> => {
  console.log(`[API PATCH] /trips/${trips_id} 수정 요청 데이터:`, updatedFields);

  const trips = readStorage<Record<string, TripResponse>>(TRIP_STORAGE_KEY, {});
  const existingTrip = trips[trips_id];

  if (!existingTrip) {
    console.warn(`404 {"detail": "Trip not found"}`);
    return { success: false, data: null };
  }

  const updatedTrip = { ...existingTrip, ...updatedFields };
  trips[trips_id] = updatedTrip;

  const attempts = readStorage<Record<string, TripAttemptResponse>>(ATTEMPT_STORAGE_KEY, {});
  const attempt = attempts[trips_id];
  if (attempt) {
    updatedTrip.attemptId = attempt.id;
    updatedTrip.attemptStatus = attempt.status;
  }

  writeStorage(TRIP_STORAGE_KEY, trips);
  writeStorage(ATTEMPT_STORAGE_KEY, attempts);

  console.log(`[API PATCH] /trips/${trips_id} 수정 완료`);
  return { success: true, data: updatedTrip };
};

export const updateTripAttemptStatusApi = async (
  trips_id: string,
  status: TripAttemptStatus
): Promise<{ success: boolean; data: TripResponse | null }> => {
  console.log(`[API PATCH] /trips/${trips_id}/attempt 상태 변경 요청:`, status);

  const trips = readStorage<Record<string, TripResponse>>(TRIP_STORAGE_KEY, {});
  const existingTrip = trips[trips_id];

  if (!existingTrip) {
    console.warn(`404 {"detail": "Trip not found"}`);
    return { success: false, data: null };
  }

  if (!isValidAttemptStatus(status)) {
    console.warn(`[API PATCH] 허용되지 않은 attempt status: ${status}`);
    return { success: false, data: null };
  }

  const attempts = readStorage<Record<string, TripAttemptResponse>>(ATTEMPT_STORAGE_KEY, {});
  const attempt = attempts[trips_id] ?? {
    id: existingTrip.attemptId ?? generateUUID(),
    tripId: trips_id,
    status: 'started',
  };

  const updatedAttempt = { ...attempt, status };
  attempts[trips_id] = updatedAttempt;

  const updatedTrip = {
    ...existingTrip,
    attemptId: updatedAttempt.id,
    attemptStatus: updatedAttempt.status,
  };
  trips[trips_id] = updatedTrip;

  writeStorage(TRIP_STORAGE_KEY, trips);
  writeStorage(ATTEMPT_STORAGE_KEY, attempts);

  console.log(`[API PATCH] /trips/${trips_id}/attempt 상태 변경 완료:`, updatedAttempt);
  return { success: true, data: updatedTrip };
};