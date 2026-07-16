import {
  Place, createTripApi, getTripByIdApi, updateTripApi, updateTripAttemptStatusApi, CreateTripRequest, TripResponse,
} from './mapApi';

// 출발지와 목적지 좌표를 바탕으로 지도의 중간 중심축 좌표를 계산하는 함수
export const calculateCenterCoordinate = (startLat: number, startLng: number, endLat: number, endLng: number) => {
  const centerLat = (startLat + endLat) / 2;
  const centerLng = (startLng + endLng) / 2;
  return { lat: centerLat, lng: centerLng };
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