import {
  type Preferences,
  type UpdatePreferencesRequest,
  getPreferencesApi,
  updatePreferencesApi,
} from "./recommendationApi";
import {
  type Place,
  fetchPlacesFromApi,
} from "../map/mapApi";

const getTestUserId = (): string => {
  return import.meta.env.VITE_TEST_USER_ID as string;
};

const logApiError = (error: unknown, action: string) => {
  console.error(`Preferences API ${action} failed`, error);
};

export const recommendationService = {
  getPreferences: async (): Promise<Preferences | null> => {
    try {
      const response = await getPreferencesApi(getTestUserId());
      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "get");
      return null;
    }
  },

  savePreferences: async (
    preferences: Omit<UpdatePreferencesRequest, "user_id">,
  ): Promise<Preferences | null> => {
    try {
      const response = await updatePreferencesApi({
        user_id: getTestUserId(),
        ...preferences,
      });

      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "update");
      return null;
    }
  },

  getRecommendations: async (): Promise<Place[] | null> => {
    try {
      console.log("recommendations 호출 완료");

      // Recommendation API 연결 전에는 기존 Place API를 사용한다.
      return await fetchPlacesFromApi();
    } catch (error) {
      console.error("Recommendations places failed", error);
      return null;
    }
  },
};
