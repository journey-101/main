import React from "react";
import { Map, MapMarker } from "react-kakao-maps-sdk";

//객체 타입 정의
interface Destination {
  id: number;
  name: string;
  lat: number;
  lng: number;
}

//임의설정 현재 위치. 추후, 사용자 GPS 연동
const CURRENT_LOCATION = {
    name: "서울시청",
    lat: 37.5665,
    lng: 126.9780,
};

//임의 목업 데이터 정의. 추후 백엔드/DB 이전
const MOCK_DESTINATIONS = [
  { id: 1, name: "덕수궁", lat: 37.5658, lng: 126.9751 },
  { id: 2, name: "광화문광장", lat: 37.5724, lng: 126.9769 },
  { id: 3, name: "명동성당", lat: 37.5632, lng: 126.9874 },
];

export function MapComponent() {
    const [selectedDest, setSelectedDest] = useState<typeof MOCK_DESTINATIONS[0] | null>(null);

    const handleFindPath = (destination: typeof MOCK_DESTINATIONS[0]) => {
        setSelectedDest(destination);

        const pathUrl = `https://kakao.com{destination.name},${destination.lat},${destination.lng}/from/${CURRENT_LOCATION.name},${CURRENT_LOCATION.lat},${CURRENT_LOCATION.lng}`;
        window.location.href = pathUrl;
    }

  return (
    <div style={{width: "100%", height: "600px"}}>
        <div style={{
            position: "absolute",
            top: "20px",
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 10,
            backgroundColor: "rgba(255, 255, 255, 0.9)",
            padding: "15px",
            borderRadius: "10px",
            display: "flex",
            gap: "10px"
        }}>
            {MOCK_DESTINATIONS.map((dest) => (
            <button
                key={dest.id}
                onClick={() => handleFindPath(dest)}
                style={{
                padding: "10px 15px",
                backgroundColor: selectedDest?.id === dest.id ? "#fee500" : "#fff", // 카카오 노란색 포인트
                border: "1px solid #ccc",
                borderRadius: "5px",
                cursor: "pointer",
                fontWeight: "bold"
                }}
            >
                {dest.name}로 도보 길찾기
            </button>
            ))}
        </div>

        <Map
        center={{ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }} // 지도 중심 좌표 (서울시청)
        style={{
            width: "400px",
            height: "500px", // 원하는 지도 높이 설정
            zindex: 0
        }}
        level={3} // 지도 확대 레벨
        >
        <MapMarker position={{ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }}>
            <div style={{ color: "#000", padding: "5px" }}>서울시청</div>
        </MapMarker>
        
            <MapMarker key={dest.id} position={{ lat: dest.lat, lng: dest.lng }}>
                <div style={{ padding: "5px", color: "#333" }}>{dest.name}</div>
            </MapMarker>
        </Map>
    </div>
  );
}
