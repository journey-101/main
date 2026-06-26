import React, { useState } from "react";
import { Map, MapMarker } from "react-kakao-maps-sdk";

// 1. 목적지 객체의 TypeScript 타입 정의
interface Destination {
  id: number;
  name: string;
  lat: number;
  lng: number;
  path: { lat: number; lng: number }[]; 
}

// 2. 임의의 사용자 현위치 고정 (서울시청)
const CURRENT_LOCATION = {
  name: "서울시청",
  lat: 37.5665,
  lng: 126.9780,
};

// 3. 목적지 3개 목업 데이터
const MOCK_DESTINATIONS: Destination[] = [
  { 
    id: 1, 
    name: "덕수궁", 
    lat: 37.5658, 
    lng: 126.9751,
    path: [
      { lat: 37.5665, lng: 126.9780 }, // 출발: 서울시청
      { lat: 37.5662, lng: 126.9765 }, // 중간 꺾임점 1
      { lat: 37.5659, lng: 126.9755 }, // 중간 꺾임점 2
      { lat: 37.5658, lng: 126.9751 }  // 도착: 덕수궁 공식 좌표
    ]
  },
  { 
    id: 2, 
    name: "광화문광장", 
    lat: 37.5724, 
    lng: 126.9769,
    path: [
      { lat: 37.5665, lng: 126.9780 },
      { lat: 37.5685, lng: 126.9778 },
      { lat: 37.5705, lng: 126.9772 },
      { lat: 37.5724, lng: 126.9769 }
    ]
  },
  { 
    id: 3, 
    name: "명동성당", 
    lat: 37.5632, 
    lng: 126.9874,
    path: [
      { lat: 37.5665, lng: 126.9780 },
      { lat: 37.5655, lng: 126.9810 },
      { lat: 37.5640, lng: 126.9850 },
      { lat: 37.5632, lng: 126.9874 }
    ]
  },
];

export function MapComponent() {
  // 4. State 타입 명시 (Destination 또는 null)
  const [selectedDest, setSelectedDest] = useState<Destination | null>(null);
  const [mapCenter, setMapCenter] = useState({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });
  const [mapLevel, setMapLevel] = useState(4);

  const [pathUrl, setPathUrl] = useState<string | null>(null);

  // 5. 버튼 클릭 시 길찾기 URL을 생성
  const handleFindPath = (destination: Destination) => {
    setSelectedDest(destination);

    const centerLat = (CURRENT_LOCATION.lat + destination.lat) / 2;
    const centerLng = (CURRENT_LOCATION.lng + destination.lng) / 2;
    setMapCenter({ lat: centerLat, lng: centerLng });
    setMapLevel(4); // 경로가 잘 보이는 축척 레벨로 고정

    // 카카오맵 공식 도보 길찾기 URL 패턴 생성
    const pathUrl = 'https://map.kakao.com/link/by/walk/${CURRENT_LOCATION.name},${CURRENT_LOCATION.lat},${CURRENT_LOCATION.lng}/${destination.name},${destination.lat},${destination.lng}';
    
    // URL 상태만 저장하여 내부 iframe으로 띄웁니다.
    setPathUrl(pathUrl);
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
        center={mapCenter}
        style={{ width: "100%", height: "100%" }}
        level={mapLevel}
      >
        {/* 현위치 마커 (서울시청) */}
        <MapMarker position={{ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }}>
          <div style={{ padding: "5px", color: "#000", fontWeight: "bold" }}>내 현위치</div>
        </MapMarker>

        {selectedDest && (
          <Polyline
            path={selectedDest.path} // 선택된 장소의 좌표 배열 연동
            strokeWeight={6}         // 도보 가이드라인 두께
            strokeColor={"#ff5656"}   // 도보 선 색상 (빨간색)
            strokeOpacity={0.85}      // 선 투명도
            strokeStyle={"solid"}     // 선 스타일
          />
        )}
      </Map>
    </div>
  );
}
