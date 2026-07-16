export interface Place {
  id: number;
  name: string;
  address: string;
  lat: number;
  lng: number;
}

// 임의의 고정 사용자 현위치 데이터
const CURRENT_LOCATION = { name: "서울시청", lat: 37.5665, lng: 126.9780 };

// 가상의 백엔드 DB 데이터
const MOCK_PLACES: Place[] = [
  { id: 1, name: "덕수궁", address: "서울 중구 세종대로 99", lat: 37.5658, lng: 126.9751 },
  { id: 2, name: "광화문광장", address: "서울 종로구 세종대로 172", lat: 37.5724, lng: 126.9769 },
  { id: 3, name: "명동성당", address: "서울 중구 명동길 74", lat: 37.5632, lng: 126.9874 },
];

/**
 * 백엔드 /place API를 통해 장소 목록을 가져오는 함수 (추후 fetch/axios 연동)
 */
export const fetchPlacesFromApi = async (): Promise<Place[]> => {
  console.log("[백엔드 API 연동 예정] [GET] /place 호출 시점입니다.");
  
  // 현재는 가상 DB 데이터를 반환합니다.
  return MOCK_PLACES;
};

// 기기 환경 또는 고정된 출발지(현위치) 데이터를 가져오는 함수
export const getCurrentLocation = () => {
  return CURRENT_LOCATION;
};

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

// 프론트엔드 목업 검증을 위한 인메모리 가상 DB
const mockTripDatabase: Map<string, TripResponse> = new Map();
const mockAttemptDatabase: Map<string, TripAttemptResponse> = new Map();

// 가상 UUID 생성 함수
const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

// [POST] 여정 생성
export const createTripApi = async (tripData: CreateTripRequest): Promise<{ success: boolean; data: TripResponse }> => {
  console.log('[API POST] /trips 요청 데이터:', tripData);

  return new Promise((resolve) => {
    setTimeout(() => {
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

      mockTripDatabase.set(generatedId, newTrip);
      mockAttemptDatabase.set(attemptId, {
        id: attemptId,
        tripId: generatedId,
        status: 'started',
      });

      console.log(`[API POST] 여정 생성 완료 - 경로: /trips/${generatedId}`);
      resolve({ success: true, data: newTrip });
    }, 400);
  });
};

// [GET] 여정 단건 조회
export const getTripByIdApi = async (tripsId: string): Promise<{ success: boolean; data: TripResponse | null }> => {
  console.log(`[API GET] /trips/${tripsId} 호출`);

  return new Promise((resolve) => {
    setTimeout(() => {
      const trip = mockTripDatabase.get(tripsId);
      if (trip) {
        const attempt = mockAttemptDatabase.get(tripsId);
        const tripWithAttempt = {
          ...trip,
          attemptId: attempt?.id ?? trip.attemptId,
          attemptStatus: attempt?.status ?? trip.attemptStatus ?? 'started',
        };

        console.log(`[API GET] /trips/${tripsId} 조회 성공:`, tripWithAttempt);
        resolve({ success: true, data: tripWithAttempt });
      } else {
        console.warn(`[API GET] /trips/${tripsId} 데이터를 찾을 수 없습니다.`);
        resolve({ success: false, data: null });
      }
    }, 400);
  });
};

// [PATCH] 여정 수정 (후기 태그 수집용)
export const updateTripApi = async (
  tripsId: string,
  updatedFields: Partial<TripResponse>
): Promise<{ success: boolean; data: TripResponse | null }> => {
  console.log(`[API PATCH] /trips/${tripsId} 수정 요청 데이터:`, updatedFields);

  return new Promise((resolve) => {
    setTimeout(() => {
      const existingTrip = mockTripDatabase.get(tripsId);
      if (existingTrip) {
        const updatedTrip = { ...existingTrip, ...updatedFields };
        mockTripDatabase.set(tripsId, updatedTrip);

        const attempt = mockAttemptDatabase.get(tripsId);
        if (attempt) {
          updatedTrip.attemptId = attempt.id;
          updatedTrip.attemptStatus = attempt.status;
        }

        console.log(`[API PATCH] /trips/${tripsId} 수정 완료`);
        resolve({ success: true, data: updatedTrip });
      } else {
        console.warn(`404 {"detail": "Trip not found"}`);
        resolve({ success: false, data: null });
      }
    }, 400);
  });
};

export const updateTripAttemptStatusApi = async (
  tripsId: string,
  status: TripAttemptStatus
): Promise<{ success: boolean; data: TripResponse | null }> => {
  console.log(`[API PATCH] /trips/${tripsId}/attempt 상태 변경 요청:`, status);

  return new Promise((resolve) => {
    setTimeout(() => {
      const existingTrip = mockTripDatabase.get(tripsId);
      if (!existingTrip) {
        console.warn(`404 {"detail": "Trip not found"}`);
        resolve({ success: false, data: null });
        return;
      }

      if (!isValidAttemptStatus(status)) {
        console.warn(`[API PATCH] 허용되지 않은 attempt status: ${status}`);
        resolve({ success: false, data: null });
        return;
      }

      const attempt = mockAttemptDatabase.get(tripsId) ?? {
        id: existingTrip.attemptId ?? generateUUID(),
        tripId: tripsId,
        status: 'started',
      };

      const updatedAttempt = { ...attempt, status };
      mockAttemptDatabase.set(tripsId, updatedAttempt);

      const updatedTrip = {
        ...existingTrip,
        attemptId: updatedAttempt.id,
        attemptStatus: updatedAttempt.status,
      };
      mockTripDatabase.set(tripsId, updatedTrip);

      console.log(`[API PATCH] /trips/${tripsId}/attempt 상태 변경 완료:`, updatedAttempt);
      resolve({ success: true, data: updatedTrip });
    }, 400);
  });
};