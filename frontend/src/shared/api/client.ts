export async function getJson<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(path, {
    headers: {
      Accept: "application/json",
    },
  });

  return (await response.json()) as TResponse;
}
