import React, { useState } from "react";
import { Map, MapMarker, Polyline } from "react-kakao-maps-sdk";

interface Place {
  id: number;
  name: string;
  address: string;
  lat: number;
  lng: number;
}

const CURRENT_LOCATION = { name: "서울시청", lat: 37.5665, lng: 126.9780 };

const MOCK_DESTINATIONS: Place[] = [
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
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);

  const [center, setCenter] = useState({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });

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
      }}>
        <span style={{ fontSize: "13px", fontWeight: "bold", color: "#555" }}>목적지 목록:</span>
        {MOCK_PLACES.map((place) => (
          <button
            key={place.id}
            onClick={() => handleSelectPlace(place)}
            style={{
              padding: "8px 16px",
              backgroundColor: selectedPlace?.id === place.id ? "#fee500" : "#fff",
              color: "#333",
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
        {selectedPlace && (
          <button 
            onClick={() => { setSelectedPlace(null); setCenter({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }); }}
            style={{ padding: "8px 12px", backgroundColor: "#eee", border: "none", borderRadius: "20px", cursor: "pointer", fontSize: "12px", color: "#333" }}
          >
            초기화
          </button>
        )}
      </div>

      {/* 카카오맵 엔진 */}
      <Map
        center={center} // 💡 상태 분리된 독립 center 변수 연동
        style={{ width: "100%", height: "100%" }}
        level={4}
      >
        {/* 출발지 마커 */}
        <MapMarker position={{ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }}>
          <div style={{ padding: "5px", color: "#000", fontWeight: "bold", fontSize: "12px" }}>출발: 서울시청</div>
        </MapMarker>

        {/* 💡 도보 추천 경로선 그리기 구문 위치 조율 */}
        {selectedDest !== null && (
          <Polyline
            path={selectedDest.path}
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
