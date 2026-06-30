import React, { useState, useEffect } from "react";
import { Map, MapMarker, Polyline } from "react-kakao-maps-sdk";
import { Place, fetchPlacesFromApi, getCurrentLocation } from "./mapApi";
import { calculateCenterCoordinate, logSelectedPlaceDetails } from "./mapService";

export function MapComponent() {
  const CURRENT_LOCATION = getCurrentLocation();

  // 상태 관리
  const [places, setPlaces] = useState<Place[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [center, setCenter] = useState({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });
  const [mapInstance, setMapInstance] = useState<any>(null);

  // '오늘의 여행' 버튼 클릭 시 데이터 가져오기 (1번 API 파일 호출)
  const handleFetchPlaces = async () => {
    console.log("========================================");
    console.log("[프론트엔드 액션] '오늘의 여행' 버튼 클릭됨");
    console.log("========================================");
    
    const data = await fetchPlacesFromApi();
    setPlaces(data);
  };

  // 장소 목록 중 하나를 선택했을 때 데이터 가공 및 가이드 (2번 Service 파일 호출)
  const handleSelectPlace = (place: Place) => {
    setSelectedPlace(place);
    logSelectedPlaceDetails(place);

    // 중간 중심축 계산 기능 호출 후 상태 반영
    const nextCenter = calculateCenterCoordinate(
      CURRENT_LOCATION.lat,
      CURRENT_LOCATION.lng,
      place.lat,
      place.lng
    );
    setCenter(nextCenter);
  };

  // 지도 리레이아웃 타이밍 제어 효과
  useEffect(() => {
    if (mapInstance && selectedPlace) {
      setTimeout(() => {
        if (typeof mapInstance.relayout === "function") {
          mapInstance.relayout();
        }
      }, 100);
    }
  }, [selectedPlace, mapInstance]);
  
  // 모든 상태 초기화
  const handleReset = () => {
    setPlaces([]);
    setSelectedPlace(null);
    setCenter({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh" }}>
      
      {/* 상단 버튼 컨트롤러 영역 */}
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
        {places.length === 0 ? (
          <button
            onClick={handleFetchPlaces}
            style={{ padding: "10px 20px", backgroundColor: "#fee500", color: "#222", border: "none", borderRadius: "20px", cursor: "pointer", fontWeight: "bold", fontSize: "14px" }}
          >
            🚀 오늘의 여행 추천받기
          </button>
        ) : (
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
            <button onClick={handleReset} style={{ padding: "8px 12px", backgroundColor: "#eee", border: "none", borderRadius: "20px", cursor: "pointer", fontSize: "12px", color: "#333" }}>
              닫기
            </button>
          </>
        )}
      </div>

      {/* 카카오맵 렌더링 물리 공간 */}
      <Map
        center={center}
        style={{ width: "100%", height: "100%" }}
        level={4}
        onCreate={setMapInstance}
      >
        {/* 출발지 마커 */}
        <MapMarker position={{ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng }}>
          <div style={{ padding: "5px", color: "#000", fontWeight: "bold", fontSize: "12px" }}>출발: 서울시청</div>
        </MapMarker>

        {/* 목적지 마커 리스트 루프 */}
        {places.map((place) => (
          <MapMarker key={place.id} position={{ lat: place.lat, lng: place.lng }}>
            <div style={{ padding: "5px", color: "#333", fontSize: "12px" }}>{place.name}</div>
          </MapMarker>
        ))}

        {/* 가이드 라인 그리기 */}
        <Polyline
          path={selectedPlace ? [
            { lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng },
            { lat: selectedPlace.lat, lng: selectedPlace.lng }
          ] : []}
          strokeWeight={6}
          strokeColor={"#ff5656"}
          strokeOpacity={0.85}
          strokeStyle={"solid"}
        />
      </Map>
    </div>
  );
}