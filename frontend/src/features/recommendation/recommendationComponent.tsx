import { useEffect, useState } from "react";
import type { Place } from "../map/mapApi";
import { MapComponent } from "../map/MapComponent";
import { PreferenceForm } from "./preferenceForm";
import { recommendationService } from "./recommendationService";

export function RecommendationComponent() {
  const [saved, setSaved] = useState(false);
  const [preferencesLoaded, setPreferencesLoaded] = useState(false);
  const [places, setPlaces] = useState<Place[]>([]);

  useEffect(() => {
    const loadPreferences = async () => {
      const preferences = await recommendationService.getPreferences();

      if (preferences) {
        setSaved(true);
      }

      setPreferencesLoaded(true);
    };

    void loadPreferences();
  }, []);

  const handleSavePreferences = async (
    preferences: Omit<
      import("./recommendationApi").Preferences,
      "user_id"
    >,
  ) => {
    const result = await recommendationService.savePreferences(preferences);

    setSaved(Boolean(result));
  };

  const handleRecommendations = async () => {
    if (!saved) {
      return;
    }

    const result = await recommendationService.getRecommendations();

    if (result) {
      setPlaces(result);
    }
  };

  if (!preferencesLoaded) {
    return null;
  }

  return (
    <div>
      <section>
        <h2>여행 성향 입력</h2>

        <PreferenceForm onSave={handleSavePreferences} />
      </section>

      <button
        type="button"
        disabled={!saved}
        onClick={() => void handleRecommendations()}
      >
        추천
      </button>

      <section>
        <h2>추천 결과</h2>
        <p>지역: 부천</p>

        {places.map((place) => (
          <div key={place.id}>
            <p>{place.name}</p>
            <p>{place.address}</p>
          </div>
        ))}
      </section>

      <section>
        <MapComponent />
      </section>
    </div>
  );
}