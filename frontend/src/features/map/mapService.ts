import {
  type CreateAttemptRequest,
  type CreateTripRequest,
  type TripAttempt,
  type TripDetail,
  type TripListItem,
  type UpdateAttemptRequest,
  type UpdateFeedbackRequest,
  type UpdateTripRequest,
  createTripApi,
  createTripAttemptApi,
  getTripByIdApi,
  getTripsApi,
  updateTripApi,
  updateTripAttemptApi,
  updateTripFeedbackApi,
} from "./mapApi";

export const calculateCenterCoordinate = (
  startLat: number,
  startLng: number,
  endLat: number,
  endLng: number,
) => {
  const centerLat = (startLat + endLat) / 2;
  const centerLng = (startLng + endLng) / 2;

  return {
    lat: centerLat,
    lng: centerLng,
  };
};

const logApiError = (error: unknown, action: string) => {
  console.error(`Trips API ${action} failed`, error);
};

export const mapService = {
  getTrips: async (): Promise<TripListItem[] | null> => {
    try {
      const response = await getTripsApi();
      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "list");
      return null;
    }
  },

  registerTrip: async (
    tripData: CreateTripRequest,
  ): Promise<TripListItem | null> => {
    try {
      const response = await createTripApi(tripData);
      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "create");
      return null;
    }
  },

  getTripDetails: async (tripId: string): Promise<TripDetail | null> => {
    try {
      const response = await getTripByIdApi(tripId);
      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "detail");
      return null;
    }
  },

  modifyTrip: async (
    tripId: string,
    tripData: UpdateTripRequest,
  ): Promise<TripListItem | null> => {
    try {
      const response = await updateTripApi(tripId, tripData);
      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "trip update");
      return null;
    }
  },

  createAttempt: async (
    tripId: string,
    attemptData: CreateAttemptRequest = {},
  ): Promise<TripAttempt | null> => {
    try {
      const response = await createTripAttemptApi(tripId, attemptData);
      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "attempt create");
      return null;
    }
  },

  modifyAttempt: async (
    tripId: string,
    attemptId: string,
    attemptData: UpdateAttemptRequest,
  ): Promise<TripAttempt | null> => {
    try {
      const response = await updateTripAttemptApi(
        tripId,
        attemptId,
        attemptData,
      );

      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "attempt update");
      return null;
    }
  },

  modifyFeedback: async (
    tripId: string,
    attemptId: string,
    feedbackData: UpdateFeedbackRequest,
  ): Promise<TripAttempt | null> => {
    try {
      const response = await updateTripFeedbackApi(
        tripId,
        attemptId,
        feedbackData,
      );

      return response.success ? response.data : null;
    } catch (error) {
      logApiError(error, "feedback update");
      return null;
    }
  },
};
