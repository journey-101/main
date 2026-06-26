import React from "react";
import { Map, MapMarker } from "react-kakao-maps-sdk";

export function MapComponent() {
  return (
    <Map
      center={{ lat: 37.5665, lng: 126.9780 }} // 지도 중심 좌표 (서울시청)
      style={{
        width: "400px",
        height: "500px", // 원하는 지도 높이 설정
      }}
      level={3} // 지도 확대 레벨
    >
      {/* 지도 위에 마커를 표시하고 싶다면 추가 */}
      <MapMarker position={{ lat: 37.5665, lng: 126.9780 }}>
        <div style={{ color: "#000", padding: "5px" }}>서울시청</div>
      </MapMarker>
    </Map>
  );
}
