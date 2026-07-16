import {
  Place, createTripApi, getTripByIdApi, updateTripApi, updateTripAttemptStatusApi, CreateTripRequest, TripResponse,
} from './mapApi';

// 출발지와 목적지 좌표를 바탕으로 지도의 중간 중심축 좌표를 계산하는 함수
export const calculateCenterCoordinate = (startLat: number, startLng: number, endLat: number, endLng: number) => {
  const centerLat = (startLat + endLat) / 2;
  const centerLng = (startLng + endLng) / 2;
  return { lat: centerLat, lng: centerLng };
};

// 목적지가 선택되었을 때 백엔드 가이드 로그를 남기는 함수
export const logSelectedPlaceDetails = (place: Place) => {
  console.log(`========================================`);
  console.log(`[프론트엔드 액션] 사용자가 목적지를 선택했습니다.`);
  console.log(`[목적지 명칭] ${place.name}`);
  console.log(`[백엔드 API 연동 데이터]조회 대상 주소: ${place.address}`);
  console.log(`[연동 가이드] 추후 /place?address=${encodeURIComponent(place.address)} 형태로 Fetch 예정`);
  console.log(`========================================`);
};

export const mapService = {
  // 1. 여정 등록 실행
  registerTrip: async (tripData: CreateTripRequest): Promise<TripResponse | null> => {
    try {
      const response = await createTripApi(tripData);
      return response.success ? response.data : null;
    } catch (error) {
      console.error('Service Error - registerTrip:', error);
      throw error;
    }
  },

  // 2. 단건 여정 상세 조회 (/trips/{trips_id})
  getTripDetails: async (tripsId: string): Promise<TripResponse | null> => {
    try {
      const response = await getTripByIdApi(tripsId);
      return response.success ? response.data : null;
    } catch (error) {
      console.error('Service Error - getTripDetails:', error);
      throw error;
    }
  },

  // 3. 동일 경로 여정 수정 (후기 태그 등 업데이트)
  modifyTrip: async (tripsId: string, fieldsToUpdate: Partial<TripResponse>): Promise<TripResponse | null> => {
    try {
      const response = await updateTripApi(tripsId, fieldsToUpdate);
      return response.success ? response.data : null;
    } catch (error) {
      console.error('Service Error - modifyTrip:', error);
      throw error;
    }
  },

  completeTripAttempt: async (tripsId: string): Promise<TripResponse | null> => {
    try {
      const response = await updateTripAttemptStatusApi(tripsId, 'completed');
      return response.success ? response.data : null;
    } catch (error) {
      console.error('Service Error - completeTripAttempt:', error);
      throw error;
    }
  },
  
  abortTripAttempt: async (tripsId: string): Promise<TripResponse | null> => {
    try {
      const response = await updateTripAttemptStatusApi(tripsId, 'aborted');
      return response.success ? response.data : null;
    } catch (error) {
      console.error('Service Error - abortTripAttempt:', error);
      throw error;
    }
  },
};