export type ApiError = {
  code: string;
  message: string;
};

export type SuccessResponse<TData> = {
  success: true;
  data: TData;
};

export type ErrorResponse = {
  success: false;
  error: ApiError;
};

export type ServiceHealthData = {
  status: string;
  service: string;
};

export type DatabaseHealthData = {
  status: string;
  db: string;
  result: number;
};

export type ServiceHealthResponse = SuccessResponse<ServiceHealthData> | ErrorResponse;
export type DatabaseHealthResponse =
  | SuccessResponse<DatabaseHealthData>
  | ErrorResponse;
export type HealthApiResponse = ServiceHealthResponse | DatabaseHealthResponse;
