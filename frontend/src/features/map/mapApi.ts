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
  console.log("========================================");
  console.log("[백엔드 API 연동 예정] [GET] /place 호출 시점입니다.");
  console.log("========================================");
  
  // 현재는 가상 DB 데이터를 반환합니다.
  return MOCK_PLACES;
};

/**
 * 기기 환경 또는 고정된 출발지(현위치) 데이터를 가져오는 함수
 */
export const getCurrentLocation = () => {
  return CURRENT_LOCATION;
};