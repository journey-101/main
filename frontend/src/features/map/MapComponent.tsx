import React, { useState } from "react";
import { Map, MapMarker, Polyline } from "react-kakao-maps-sdk";

interface Destination {
  id: number;
  name: string;
  lat: number;
  lng: number;
  path: { lat: number; lng: number }[]; 
}

const CURRENT_LOCATION = { name: "서울시청", lat: 37.5665, lng: 126.9780 };

const MOCK_DESTINATIONS: Destination[] = [
  { 
    id: 1, 
    name: "덕수궁", 
    lat: 37.5658, 
    lng: 126.9751,
    path: [
      { lat: 37.5665, lng: 126.9780 },
      { lat: 37.5662, lng: 126.9765 },
      { lat: 37.5659, lng: 126.9755 },
      { lat: 37.5658, lng: 126.9751 }
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
  const [selectedDest, setSelectedDest] = useState<Destination | null>(null);
  
  // 💡 [해결 핵심] 지도의 중심 좌표 객체를 상수로 바로 넣지 않고, 별도 독립 상태로 분리하여 렌더링 충돌 방지
  const [center, setCenter] = useState({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });

  const handleFindPath = (destination: Destination) => {
    // 1. 선택된 목적지 데이터 할당
    setSelectedDest(destination);

    // 2. 출발지와 목적지의 중간값 계산 후 지도의 중심축 이동 명령
    const centerLat = (CURRENT_LOCATION.lat + destination.lat) / 2;
    const centerLng = (CURRENT_LOCATION.lng + destination.lng) / 2;
    setCenter({ lat: centerLat, lng: centerLng });
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh" }}>
      
      {/* 상단 장소 선택 버튼 바 */}
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
        <span style={{ fontSize: "13px", fontWeight: "bold", color: "#555" }}>도보 안내:</span>
        {MOCK_DESTINATIONS.map((dest) => (
          <button
            key={dest.id}
            onClick={() => handleFindPath(dest)}
            style={{
              padding: "8px 16px",
              backgroundColor: selectedDest?.id === dest.id ? "#ff5656" : "#fff",
              color: selectedDest?.id === dest.id ? "#fff" : "#333",
              border: "1px solid #e0e0e0",
              borderRadius: "20px",
              cursor: "pointer",
              fontWeight: "bold",
              fontSize: "13px"
            }}
          >
            {dest.name}
          </button>
        ))}
        {selectedDest && (
          <button 
            onClick={() => { setSelectedDest(null); setCenter({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }); }}
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
