import React, { useState } from "react";
import { Map, MapMarker } from "react-kakao-maps-sdk";

// 1. 목적지 객체의 TypeScript 타입 정의
interface Destination {
  id: number;
  name: string;
  lat: number;
  lng: number;
}

// 2. 임의의 사용자 현위치 고정 (서울시청)
const CURRENT_LOCATION = {
  name: "서울시청",
  lat: 37.5665,
  lng: 126.9780,
};

// 3. 목적지 3개 목업 데이터
const MOCK_DESTINATIONS: Destination[] = [
  { id: 1, name: "덕수궁", lat: 37.5658, lng: 126.9751 },
  { id: 2, name: "광화문광장", lat: 37.5724, lng: 126.9769 },
  { id: 3, name: "명동성당", lat: 37.5632, lng: 126.9874 },
];

export function MapComponent() {
  // 4. State 타입 명시 (Destination 또는 null)
  const [selectedDest, setSelectedDest] = useState<Destination | null>(null);

  // 5. 버튼 클릭 시 길찾기 URL을 생성하고 새 창 또는 현재 페이지로 이동
  const handleFindPath = (destination: Destination) => {
    setSelectedDest(destination);

    // 카카오맵 공식 도보 길찾기 URL 패턴 생성
    const pathUrl = `https://map.kakao.com/link/by/walk/${CURRENT_LOCATION.name},${CURRENT_LOCATION.lat},${CURRENT_LOCATION.lng}/${destination.name},${destination.lat},${destination.lng}';
    
    // 현재 창에서 바로 카카오맵 길찾기 모바일 페이지로 전환
    window.location.assign(pathUrl);
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh" }}>
      
      {/* 장소 선택 버튼 레이아웃 */}
      <div style={{
        position: "absolute",
        top: "20px",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 10,
        backgroundColor: "rgba(255, 255, 255, 0.9)",
        padding: "15px",
        borderRadius: "10px",
        boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
        display: "flex",
        gap: "10px"
      }}>
        {MOCK_DESTINATIONS.map((dest) => (
          <button
            key={dest.id}
            onClick={() => handleFindPath(dest)}
            style={{
              padding: "10px 15px",
              backgroundColor: selectedDest?.id === dest.id ? "#fee500" : "#fff",
              border: "1px solid #ccc",
              borderRadius: "5px",
              cursor: "pointer",
              fontWeight: "bold",
              color: "#000"
            }}
          >
            {dest.name}
          </button>
        ))}
      </div>

      {/* 카카오맵 렌더링 영역 */}
      <Map
        center={{ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }}
        style={{ width: "100%", height: "100%" }}
        level={4}
      >
        {/* 현위치 마커 (서울시청) */}
        <MapMarker position={{ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }}>
          <div style={{ padding: "5px", color: "#000", fontWeight: "bold" }}>내 현위치</div>
        </MapMarker>
      </Map>
    </div>
  );
}
