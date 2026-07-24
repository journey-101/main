import React, { useEffect, useState } from "react";
import { Map, MapMarker, Polyline } from "react-kakao-maps-sdk";
import {
  type CreateTripRequest,
  type Place,
  type TripAttemptStatus,
  type TripDetail,
  type TripListItem,
  fetchPlacesFromApi,
  getCurrentLocation,
} from "./mapApi";
import { calculateCenterCoordinate, mapService } from "./mapService";

export function MapComponent() {
  const CURRENT_LOCATION = getCurrentLocation();

  // 상태 관리
  const [places, setPlaces] = useState<Place[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [center, setCenter] = useState({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });
  const [mapInstance, setMapInstance] = useState<any>(null);
  const [placeError, setPlaceError] = useState<string | null>(null);
  const [trips, setTrips] = useState<TripListItem[]>([]);
  const [selectedTrip, setSelectedTrip] = useState<TripDetail | null>(null);
  const [selectedAttemptId, setSelectedAttemptId] = useState<string | null>(null);

  // '오늘의 여행' 버튼 클릭 시 데이터 가져오기 (1번 API 파일 호출)
  const handleFetchPlaces = async () => {
    console.log("[프론트엔드 액션] '오늘의 여행' 버튼 클릭됨");

    setPlaceError(null);
    try {
      const data = await fetchPlacesFromApi();
      setPlaces(data);
      setSelectedPlace(null);
      setCenter({ lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng });
    } catch (error) {
      console.error(error);
      setPlaceError("장소 데이터를 불러오지 못했습니다.");
    }
  };

  // 장소 목록 중 하나를 선택했을 때 데이터 가공 및 가이드 (2번 Service 파일 호출)
  const handleSelectPlace = (place: Place) => {
    const selectedRoutePlace: Place = place;
    setSelectedPlace(selectedRoutePlace);

    const nextCenter = calculateCenterCoordinate(
      CURRENT_LOCATION.lat,
      CURRENT_LOCATION.lng,
      selectedRoutePlace.lat,
      selectedRoutePlace.lng
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
    setPlaceError(null);
  };

  // 여정 목업 데이터
  const [tripFormData, setTripFormData] = useState<CreateTripRequest>({
    user_id: import.meta.env.VITE_TEST_USER_ID as string,
    title: "",
  });
  const [tripTitle, setTripTitle] = useState("");
  const [attemptStatus, setAttemptStatus] =
    useState<TripAttemptStatus>("started");
  const [feedbackText, setFeedbackText] = useState("");
  const [tagInput, setTagInput] = useState("");

  useEffect(() => {
    const loadTrips = async () => {
      const result = await mapService.getTrips();

      if (result) {
        setTrips(result);
      }
    };

    void loadTrips();
  }, []);

  const getCurrentAttempt = () => {
    if (!selectedTrip || !selectedAttemptId) {
      return null;
    }

    return (
      selectedTrip.attempts.find(
        (attempt) => attempt.id === selectedAttemptId,
      ) ?? null
    );
  };

  const refreshSelectedTrip = async (
    tripId: string,
    attemptId: string | null = selectedAttemptId,
  ) => {
    const detail = await mapService.getTripDetails(tripId);

    if (!detail) {
      return;
    }

    setSelectedTrip(detail);
    setTripTitle(detail.title);

    if (!attemptId) {
      return;
    }

    const attempt = detail.attempts.find(
      (item) => item.id === attemptId,
    );

    if (attempt) {
      setSelectedAttemptId(attempt.id);
      setAttemptStatus(attempt.status);
      setFeedbackText(attempt.feedback_text ?? "");
    }
  };

  const handleCreateTrip = async () => {
    const result = await mapService.registerTrip(tripFormData);

    if (!result) {
      return;
    }

    const attemptId = result.current_attempt.id;

    setTrips((prev) => [result, ...prev]);
    setSelectedAttemptId(attemptId);
    setSelectedTrip(null);

    await refreshSelectedTrip(result.id, attemptId);
  };

  const handleSelectTrip = async (trip: TripListItem) => {
    const attemptId = trip.current_attempt.id;

    setSelectedAttemptId(attemptId);
    setSelectedTrip(null);

    await refreshSelectedTrip(trip.id, attemptId);
  };

const handleUpdateTrip = async () => {
  if (!selectedTrip) {
    return;
  }

  const attempt = getCurrentAttempt();

  if (!attempt) {
    return;
  }

  const tripResult = await mapService.modifyTrip(selectedTrip.id, {
    title: tripTitle,
  });

  if (!tripResult) {
    return;
  }

  const attemptResult = await mapService.modifyAttempt(
    selectedTrip.id,
    attempt.id,
    {
      status: attemptStatus,
      feedback_text: feedbackText,
    },
  );

  if (!attemptResult) {
    return;
  }

  const feedbackResult = await mapService.modifyFeedback(
    selectedTrip.id,
    attempt.id,
    {
      feedback_text: feedbackText,
    },
  );

  if (!feedbackResult) {
    return;
  }

  setTrips((prev) =>
    prev.map((trip) =>
      trip.id === tripResult.id ? tripResult : trip,
    ),
  );

  await refreshSelectedTrip(selectedTrip.id, attempt.id);
};

  const handleAddUserTag = () => {
    const normalizedTag = tagInput.trim();

    if (!normalizedTag) {
      return;
    }

    setFeedbackText((prev) => {
      if (!prev.trim()) {
        return `#${normalizedTag}`;
      }

      return `${prev.trim()} #${normalizedTag}`;
    });

    setTagInput("");
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
            {/* 6) UI에 장소 목록 카드 형태로 표시 */}
            {places.length > 0 && (
              <div
                style={{
                  position: "absolute",
                  bottom: "20px",
                  left: "20px",
                  zIndex: 10,
                  width: "320px",
                  maxHeight: "280px",
                  overflowY: "auto",
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  borderRadius: "16px",
                  padding: "14px",
                  boxShadow: "0 6px 20px rgba(0,0,0,0.18)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                  <strong style={{ fontSize: "14px" }}>추천 장소</strong>
                  <span style={{ fontSize: "12px", color: "#64748b" }}>{places.length}개</span>
                </div>

                {placeError && (
                  <div style={{ color: "#dc2626", fontSize: "12px", marginBottom: "8px" }}>
                    {placeError}
                  </div>
                )}

                {places.map((place) => (
                  <button
                    key={place.id}
                    onClick={() => handleSelectPlace(place)}
                    style={{
                      display: "block",
                      width: "100%",
                      textAlign: "left",
                      padding: "8px 10px",
                      marginBottom: "8px",
                      borderRadius: "10px",
                      border: selectedPlace?.id === place.id ? "1px solid #ff5656" : "1px solid #e2e8f0",
                      backgroundColor: selectedPlace?.id === place.id ? "#fff5f5" : "#fff",
                      cursor: "pointer",
                    }}
                  >
                    <div style={{ fontWeight: "bold", fontSize: "13px", color: "#111827" }}>{place.name}</div>
                    <div style={{ fontSize: "12px", color: "#64748b", marginTop: "2px" }}>
                      {place.address || "주소 정보 없음"}
                    </div>
                  </button>
                ))}
              </div>
            )}
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
          <div style={{ padding: "5px", color: "#000", fontWeight: "bold", fontSize: "12px" }}>출발: 인천지방법원부천지원</div>
        </MapMarker>

        {/* 가이드 라인 그리기 */}
        {selectedPlace && (
          <>
            <Polyline
              path={[
                { lat: CURRENT_LOCATION.lat, lng: CURRENT_LOCATION.lng },
                { lat: selectedPlace.lat, lng: selectedPlace.lng },
              ]}
              strokeWeight={6}
              strokeColor={"#ff5656"}
              strokeOpacity={0.85}
              strokeStyle={"solid"}
            />
            <MapMarker position={{ lat: selectedPlace.lat, lng: selectedPlace.lng }}>
              <div style={{ padding: "5px", color: "#000", fontWeight: "bold", fontSize: "12px" }}>
                {selectedPlace.name}
              </div>
            </MapMarker>
          </>
        )}
      </Map>

            <section
                style={{
                  marginTop: "24px",
                  padding: "16px",
                  border: "1px solid #e2e8f0",
                  borderRadius: "12px",
                  backgroundColor: "#ffffff",
                }}
              >
              <h2 style={{ margin: "0 0 12px" }}>Trips</h2>

              <div
                style={{
                  display: "flex",
                  gap: "8px",
                  marginBottom: "16px",
                }}
              >
                <input
                  type="text"
                  value={tripFormData.title}
                  onChange={(event) =>
                    setTripFormData((prev) => ({
                      ...prev,
                      title: event.target.value,
                    }))
                  }
                  placeholder="여행 제목"
                  style={{
                    flex: 1,
                    padding: "10px",
                    border: "1px solid #cbd5e1",
                    borderRadius: "6px",
                  }}
                />

                <button
                  type="button"
                  onClick={handleCreateTrip}
                  style={{
                    padding: "10px 14px",
                    border: 0,
                    borderRadius: "6px",
                    backgroundColor: "#2563eb",
                    color: "#fff",
                    cursor: "pointer",
                  }}
                >
                  Trip 생성
                </button>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
                  gap: "10px",
                }}
              >
                {trips.map((trip) => (
                  <button
                    key={trip.id}
                    type="button"
                    onClick={() => void handleSelectTrip(trip)}
                    style={{
                      padding: "14px",
                      textAlign: "left",
                      border: "1px solid #cbd5e1",
                      borderRadius: "10px",
                      backgroundColor:
                        selectedTrip?.id === trip.id ? "#eff6ff" : "#fff",
                      cursor: "pointer",
                    }}
                  >
                    <strong>{trip.title}</strong>
                    <div
                      style={{
                        marginTop: "8px",
                        fontSize: "13px",
                        color: "#64748b",
                      }}
                    >
                      상태: {trip.current_attempt.status}
                    </div>
                  </button>
                ))}
              </div>

              {selectedTrip && (
                <section
                  style={{
                    marginTop: "20px",
                    paddingTop: "16px",
                    borderTop: "1px solid #e2e8f0",
                  }}
                >
                  <h3 style={{ margin: "0 0 12px" }}>선택된 Trip</h3>

                  <div
                    style={{
                      display: "flex",
                      gap: "8px",
                      marginBottom: "16px",
                    }}
                  >
                    <input
                      type="text"
                      value={tripTitle}
                      onChange={(event) => setTripTitle(event.target.value)}
                      style={{
                        flex: 1,
                        padding: "10px",
                        border: "1px solid #cbd5e1",
                        borderRadius: "6px",
                      }}
                    />

                    <button
                      type="button"
                      onClick={() => void handleUpdateTrip()}
                      style={{
                        padding: "10px 14px",
                        border: 0,
                        borderRadius: "6px",
                        backgroundColor: "#475569",
                        color: "#fff",
                        cursor: "pointer",
                      }}
                    >
                      제목 수정
                    </button>
                  </div>

                  {getCurrentAttempt() && (
                    <div
                      style={{
                        padding: "14px",
                        border: "1px solid #e2e8f0",
                        borderRadius: "8px",
                      }}
                    >
                      <h4 style={{ margin: "0 0 12px" }}>Attempt 수정</h4>

                      <label
                        style={{
                          display: "block",
                          marginBottom: "10px",
                        }}
                      >
                        상태
                        <select
                          value={attemptStatus}
                          onChange={(event) =>
                            setAttemptStatus(
                              event.target.value as TripAttemptStatus,
                            )
                          }
                          style={{
                            display: "block",
                            marginTop: "6px",
                            padding: "8px",
                            border: "1px solid #cbd5e1",
                            borderRadius: "6px",
                          }}
                        >
                          <option value="started">started</option>
                          <option value="completed">completed</option>
                          <option value="aborted">aborted</option>
                        </select>
                      </label>

                      <label
                        style={{
                          display: "block",
                          marginBottom: "10px",
                        }}
                      >
                        후기
                        <textarea
                          value={feedbackText}
                          onChange={(event) => setFeedbackText(event.target.value)}
                          rows={4}
                          style={{
                            display: "block",
                            width: "100%",
                            marginTop: "6px",
                            padding: "8px",
                            boxSizing: "border-box",
                            border: "1px solid #cbd5e1",
                            borderRadius: "6px",
                            resize: "vertical",
                          }}
                        />
                      </label>

                      <div
                        style={{
                          marginTop: "18px",
                          paddingTop: "14px",
                          borderTop: "1px dashed #cbd5e1",
                        }}
                        >
                        <h4 style={{ margin: "0 0 10px" }}>Feedback 수정</h4>

                        <div
                          style={{
                            display: "flex",
                            gap: "8px",
                            marginBottom: "10px",
                          }}
                        >
                          <input
                            type="text"
                            value={tagInput}
                            onChange={(event) => setTagInput(event.target.value)}
                            placeholder="사용자 입력 태그"
                            style={{
                              flex: 1,
                              padding: "8px",
                              border: "1px solid #cbd5e1",
                              borderRadius: "6px",
                            }}
                          />

                          <button
                            type="button"
                            onClick={handleAddUserTag}
                            style={{
                              padding: "8px 12px",
                              border: 0,
                              borderRadius: "6px",
                              backgroundColor: "#64748b",
                              color: "#fff",
                              cursor: "pointer",
                            }}
                          >
                            태그 추가
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </section>
              )}
            </section>
    </div>
  );
}