import React, { useState, useEffect } from "react";
import { Map, MapMarker, Polyline } from "react-kakao-maps-sdk";
import { Place, fetchPlacesFromApi, getCurrentLocation, CreateTripRequest, TripResponse } from "./mapApi";
import { calculateCenterCoordinate, logSelectedPlaceDetails, mapService } from "./mapService";

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

  // 여정 목업 데이터
  const [tripFormData, setTripFormData] = useState<CreateTripRequest>({
    title: '서울 혼자 연습 여행',
    origin_region_code: 'KR-41',
    destination_region_code: 'KR-11',
  });

  // 조회 및 검증 단계 흐름 제어용 상탯값
  const [lastCreatedId, setLastCreatedId] = useState<string>(''); // 생성된 uuid 보관
  const [fetchedTrip, setFetchedTrip] = useState<TripResponse | null>(null); // GET 결과 보관
  const [tagInput, setTagInput] = useState<string>(''); // 추가할 후기 태그 문자열

  // 폼 필드 입력 헬퍼 함수
  const handleFieldChange = (key: keyof CreateTripRequest, value: any) => {
    setTripFormData((prev) => ({ ...prev, [key]: value }));
  };

  // 여정 POST 호출
  const handlePostTrip = async () => {
    console.log('[UI Action] 목적지 선택 완료 -> 여정 생성(POST) 호출');
    const result = await mapService.registerTrip(tripFormData);
    
    if (result) {
      setLastCreatedId(result.id);
      setFetchedTrip(result);
      alert(`여정이 성공적으로 POST 되었습니다!\n생성된 uuid: ${result.id}\n이제 2단계 조회를 진행하세요.`);
    }
  };

  // 여정 GET 호출
  const handleGetTrip = async () => {
    if (!lastCreatedId) {
      alert('생성된 여정 uuid가 없습니다. 먼저 1단계 여정 생성을 실행해 주세요.');
      return;
    }

    console.log(`[UI Action] 여정 조회(GET) 호출 -> ID: ${lastCreatedId}`);
    const result = await mapService.getTripDetails(lastCreatedId);
    
    if (result) {
      setFetchedTrip(result);
    }
  };

  // 여정 PATCH 호출
  const handlePatchTripTags = async () => {
    if (!fetchedTrip) {
      alert('조회된 여정 데이터가 없습니다. 먼저 2단계 조회를 실행해 주세요.');
      return;
    }
    if (!tagInput.trim()) return;

    const updatedTags = [...fetchedTrip.feedback_text, tagInput.trim()];
    console.log(`[UI Action] 여정 후기 태그 수정(PATCH) 호출 -> ID: ${fetchedTrip.id}`);

    const result = await mapService.modifyTrip(fetchedTrip.id, { feedback_text: updatedTags });
    if (result) {
      setFetchedTrip(result);
      setTagInput('');
    }
  };

  const handleCompleteAttempt = async () => {
    const targetTripId = fetchedTrip?.id || lastCreatedId;
    if (!targetTripId) {
      alert('여정이 생성되지 않았습니다. 먼저 여정을 생성해 주세요.');
      return;
    }

    console.log(`[UI Action] 여정 attempt 완료(PATCH) 호출 -> ID: ${targetTripId}`);
    const result = await mapService.completeTripAttempt(targetTripId);

    if (result) {
      setFetchedTrip(result);
    }
  };

  const handleAbortAttempt = async () => {
    const targetTripId = fetchedTrip?.id || lastCreatedId;
    if (!targetTripId) {
      alert('여정이 생성되지 않았습니다. 먼저 여정을 생성해 주세요.');
      return;
    }

    console.log(`[UI Action] 여정 attempt 일시중단(PATCH) 호출 -> ID: ${targetTripId}`);
    const result = await mapService.abortTripAttempt(targetTripId);

    if (result) {
      setFetchedTrip(result);
    }
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

      {/* 1단계: 여정 생성 */}
      <div style={{ marginBottom: '25px', padding: '15px', border: '1px solid #ddd', borderRadius: '6px' }}>
        <h3 style={{ margin: '0 0 10px 0', color: '#e67e22' }}>1. 여정 생성 (POST /trips)</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px', fontSize: '14px' }}>
          <label>여행 제목: <input type="text" value={tripFormData.title} onChange={e => handleFieldChange('title', e.target.value)} /></label>
        </div>
        <button onClick={handlePostTrip} style={{ padding: '8px 16px', backgroundColor: '#e67e22', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          목적지 선택 및 여정 생성 (POST)
        </button>
      </div>

      {/* 2단계 및 3단계: 조회 및 동일 경로 수정 */}
      <div style={{ padding: '15px', border: '1px solid #2980b9', borderRadius: '6px', backgroundColor: '#f4f9fc' }}>
        <h3 style={{ margin: '0 0 10px 0', color: '#2980b9' }}>2 & 3. 여정 상세조회 및 태그 수정 (/trips/{"{uuid}"})</h3>
        
        <div style={{ marginBottom: '15px' }}>
          <button onClick={handleGetTrip} style={{ padding: '8px 16px', backgroundColor: '#2980b9', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', marginRight: '10px' }}>
            여정 상세 조회 (GET)
          </button>
        </div>

        {fetchedTrip ? (
          <div style={{ background: '#fff', padding: '15px', borderRadius: '4px', border: '1px solid #cbd5e1' }}>
            <h4 style={{ margin: '0 0 8px 0' }}>📄 백엔드 수신 데이터 결과</h4>
            <pre style={{ background: '#f8fafc', padding: '10px', borderRadius: '4px', fontSize: '12px', overflowX: 'auto' }}>
              {JSON.stringify(fetchedTrip, null, 2)}
            </pre>

            <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px dashed #cbd5e1' }}>
              <div
                style={{
                  marginBottom: '10px',
                  fontWeight: 'bold',
                  color:
                    fetchedTrip.attemptStatus === 'completed'
                      ? '#059669'
                      : fetchedTrip.attemptStatus === 'aborted'
                      ? '#dc2626'
                      : '#d97706',
                }}
              >
                현재 attempt 상태: {fetchedTrip.attemptStatus ?? 'started'}
              </div>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                <button onClick={handleCompleteAttempt} style={{ padding: '8px 12px', backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  완료
                </button>
                <button onClick={handleAbortAttempt} style={{ padding: '8px 12px', backgroundColor: '#dc2626', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  일시중단
                </button>
              </div>
            </div>

            <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px dashed #cbd5e1' }}>
              <h4 style={{ margin: '0 0 8px 0' }}>🏷️ 후기 태그 수집용 컴포넌트</h4>
              <div style={{ marginBottom: '10px' }}>
                {fetchedTrip.feedback_text.length === 0 ? (
                  <span style={{ color: '#94a3b8', fontSize: '13px' }}>등록된 후기 태그가 없습니다.</span>
                ) : (
                  fetchedTrip.feedback_text.map((tag, idx) => (
                    <span key={idx} style={{ backgroundColor: '#fef3c7', color: '#d97706', padding: '3px 8px', marginRight: '6px', borderRadius: '4px', fontSize: '13px', fontWeight: '5px' }}>
                      #{tag}
                    </span>
                  ))
                )}
              </div>
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                style={{ padding: '5px', width: '160px', marginRight: '6px' }}
              />
              <button onClick={handlePatchTripTags} style={{ padding: '5px 12px', backgroundColor: '#059669', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                태그 저장 (PATCH)
              </button>
            </div>
          </div>
        ) : (
          <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>여정을 먼저 생성하고 조회 버튼을 누르면 정밀 스펙이 로드됩니다.</p>
        )}
        </div>
    </div>
  );
}