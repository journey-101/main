import React, { useState } from "react";
import { Map, MapMarker, Polyline } from "react-kakao-maps-sdk";

declare global {
  interface Window {
    kakao: any;
  }
}

interface Place {
  id: number;
  name: string;
  address: string;
  lat: number;
  lng: number;
}

const CURRENT_LOCATION = { name: "서울시청", lat: 37.5665, lng: 126.9780 };

const MOCK_PLACES: Place[] = [
  { 
    id: 1, 
    name: "덕수궁", 
    lat: 37.5658, 
    lng: 126.9751
  },
  { 
    id: 2, 
    name: "광화문광장", 
    lat: 37.5724, 
    lng: 126.9769
  },
  { 
    id: 3, 
    name: "명동성당", 
    lat: 37.5632, 
    lng: 126.9874
  },
];

export function MapComponent() {
  const [places, setPlaces] = useState<Place[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [center, setCenter] = useState({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });
  const [mapInstance, setMapInstance] = useState<kakao.maps.Map | null>(null);

  // 3. [단계 1] '오늘의 여행' 버튼 클릭 시 실행되는 함수 (추후 /place API 연동 지점)
  const handleFetchPlaces = () => {
    console.log("========================================");
    console.log("[프론트엔드 액션] '오늘의 여행' 버튼 클릭됨");
    console.log("[백엔드 API 연동 예정] [GET] /place 호출 시점입니다.");
    console.log("========================================");

    // 💡 지금은 백엔드가 없으므로, 준비해 둔 가상 DB 데이터를 상태에 주입하여 화면에 노출시킵니다.
    // 추후: fetch('/place').then(res => res.json()).then(data => setPlaces(data))
    setPlaces(MOCK_PLACES);
  };

  const handleSelectPlace = (place: Place) => {
    setSelectedPlace(place);

    // 💡 [요구사항 반영] 개발자 도구 콘솔창에 주소 조회 임의 로그 출력
    console.log(`========================================`);
    console.log(`[프론트엔드 액션] 사용자가 목적지를 선택했습니다.`);
    console.log(`[목적지 명칭] ${place.name}`);
    console.log(`[백엔드 API 연동 데이터]조회 대상 주소: ${place.address}`);
    console.log(`[연동 가이드] 추후 /place?address=${encodeURIComponent(place.address)} 형태로 Fetch 예정`);
    console.log(`========================================`);

    // 지도 화면 중심을 출발지와 목적지의 중간으로 이동시켜 직선이 한눈에 보이도록 세팅
    const centerLat = (CURRENT_LOCATION.lat + place.lat) / 2;
    const centerLng = (CURRENT_LOCATION.lng + place.lng) / 2;
    setCenter({ lat: centerLat, lng: centerLng });
  };

  useEffect(() => {
    if (mapInstance && selectedPlace) {
      // 아주 미세한 시간차(0.1초)를 두고 지도를 강제로 리사이즈/재인식 시켜서 선이 그려지도록 유도합니다.
      setTimeout(() => {
        mapInstance.relayout();
      }, 100);
    }
  }, [selectedPlace, mapInstance]);
  
  // 5. 모든 상태를 처음으로 돌리는 초기화 함수
  const handleReset = () => {
    setPlaces([]);
    setSelectedPlace(null);
    setCenter({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh" }}>
      
      {/* 장소 목록 선택 버튼바 UI 레이아웃 */}
      <div style={{
        position: "absolute",
        top: "20px",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 10,
        backgroundColor: "rgba(255, 255, 255, 0.95)",
        padding: "12px 20px",
        borderRadius: "30px",
        boxShadow: "0 4px 15px rgba(0,0,0,0.15)",
        display: "flex",
        gap: "10px",
        alignItems: "center"
      }}>{places.length === 0 ? (
          <button
            onClick={handleFetchPlaces}
            style={{
              padding: "10px 20px",
              backgroundColor: "#fee500", // 카카오 고유 시그니처 옐로우
              color: "#222",
              border: "none",
              borderRadius: "20px",
              cursor: "pointer",
              fontWeight: "bold",
              fontSize: "14px"
            }}
          >
            🚀 오늘의 여행 추천받기
          </button>
        ) : (
          // 💡 [순서 반영] '오늘의 여행'을 눌러 데이터가 채워지면 아래의 장소 목록 버튼들이 나타납니다.
          <>
            <span style={{ fontSize: "13px", fontWeight: "bold", color: "#555" }}>목적지 선택:</span>
            {places.map((place) => (
              <button
                key={place.id}
                onClick={() => handleSelectPlace(place)}
                style={{
                  padding: "8px 16px",
                  backgroundColor: selectedPlace?.id === place.id ? "#ff5656" : "#fff",
                  color: selectedPlace?.id === place.id ? "#fff" : "#333",
                  border: "1px solid #e0e0e0",
                  borderRadius: "20px",
                  cursor: "pointer",
                  fontWeight: "bold",
                  fontSize: "13px"
                }}
              >
                {place.name}
              </button>
            ))}
            <button 
              onClick={handleReset}
              style={{ padding: "8px 12px", backgroundColor: "#eee", border: "none", borderRadius: "20px", cursor: "pointer", fontSize: "12px", color: "#333" }}
            >
              닫기
            </button>
          </>
        )}
      </div>

      {/* 카카오맵 엔진 */}
      <Map
        center={center} // 💡 상태 분리된 독립 center 변수 연동
        style={{ width: "100%", height: "600px" }}
        level={4}
        onCreate={setMapInstance}
      >
        {/* 출발지 마커 */}
        <MapMarker position={{ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }}>
          <div style={{ padding: "5px", color: "#000", fontWeight: "bold", fontSize: "12px" }}>출발: 서울시청</div>
        </MapMarker>

        {/* 💡 도보 추천 경로선 그리기 구문 위치 조율 */}
        {selectedPlace !== null && (
          <Polyline
            path={[
                {lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng},
                {lat: selectedPlace.lat, lng: selectedPlace.lat}
            ]}
            strokeWeight={6}
            strokeColor={"#ff5656"}
            strokeOpacity={0.85}
            strokeStyle={"solid"}
          />
        )}
      </Map>
    </div>
  );
}
