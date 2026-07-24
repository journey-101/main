import { useEffect, useState } from "react";
import type { Preferences } from "./recommendationApi";

interface PreferenceFormProps {
  initialPreferences?: Preferences | null;
  onSave: (
    preferences: Omit<Preferences, "user_id">,
  ) => Promise<void>;
}

const PREFERRED_CATEGORIES = [
  "여유 있는 한적한 야외",
  "조용하고 아늑한 실내",
  "오가기 편리한 곳",
  "혼자 있어도 어색하지 않은 공간",
  "가볍게 다닐 수 있는 동네 산책로",
];

const AVOIDED_CATEGORIES = [
  "사람이 너무 많은 핫플레이스",
  "방문 절차가 복잡한 곳",
  "오래 걷는 골목길",
  "직원이 자주 말을 거는 곳",
  "중간에 휴식이 어려운 곳",
];

const DEFAULT_PREFERENCES: Omit<Preferences, "user_id"> = {
  preferred_categories: [],
  avoided_categories: [],
  prefers_quiet: false,
  max_walk_minutes: 30,
  is_first_time_traveler: false,
};

export function PreferenceForm({
  initialPreferences,
  onSave,
}: PreferenceFormProps) {
  const [formData, setFormData] = useState<
    Omit<Preferences, "user_id">
  >(DEFAULT_PREFERENCES);

  useEffect(() => {
    if (!initialPreferences) {
      return;
    }

    const { user_id: _userId, ...savedPreferences } = initialPreferences;
    setFormData(savedPreferences);
  }, [initialPreferences]);

  const toggleCategory = (
    field: "preferred_categories" | "avoided_categories",
    category: string,
  ) => {
    setFormData((previous) => {
      const categories = previous[field];

      return {
        ...previous,
        [field]: categories.includes(category)
          ? categories.filter((item) => item !== category)
          : [...categories, category],
      };
    });
  };

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void onSave(formData);
      }}
    >
      <fieldset>
        <legend>선호하는 여행 성향</legend>

        {PREFERRED_CATEGORIES.map((category) => (
          <label key={category} style={{ display: "block" }}>
            <input
              type="checkbox"
              checked={formData.preferred_categories.includes(category)}
              onChange={() =>
                toggleCategory("preferred_categories", category)
              }
            />
            {category}
          </label>
        ))}
      </fieldset>

      <fieldset>
        <legend>피하고 싶은 여행 성향</legend>

        {AVOIDED_CATEGORIES.map((category) => (
          <label key={category} style={{ display: "block" }}>
            <input
              type="checkbox"
              checked={formData.avoided_categories.includes(category)}
              onChange={() =>
                toggleCategory("avoided_categories", category)
              }
            />
            {category}
          </label>
        ))}
      </fieldset>

      <label style={{ display: "block" }}>
        <input
          type="checkbox"
          checked={formData.prefers_quiet}
          onChange={(event) =>
            setFormData((previous) => ({
              ...previous,
              prefers_quiet: event.target.checked,
            }))
          }
        />
        조용한 장소를 선호합니다
      </label>

      <label style={{ display: "block" }}>
        최대 도보 시간: {formData.max_walk_minutes}분
        <input
          type="range"
          min={10}
          max={60}
          step={10}
          value={formData.max_walk_minutes}
          onChange={(event) =>
            setFormData((previous) => ({
              ...previous,
              max_walk_minutes: Number(event.target.value),
            }))
          }
        />
      </label>

      <label style={{ display: "block" }}>
        <input
          type="checkbox"
          checked={formData.is_first_time_traveler}
          onChange={(event) =>
            setFormData((previous) => ({
              ...previous,
              is_first_time_traveler: event.target.checked,
            }))
          }
        />
        처음 여행하는 장소입니다
      </label>

      <button type="submit">저장</button>
    </form>
  );
}