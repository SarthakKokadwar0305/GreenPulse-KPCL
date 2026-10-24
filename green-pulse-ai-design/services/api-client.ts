const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL
const MOCK_LATENCY_MS = 450

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type MockModule = { default: unknown }

/**
 * Resolves data from the FastAPI backend when NEXT_PUBLIC_API_BASE_URL is set,
 * otherwise falls back to the bundled JSON fixture. Service signatures and
 * response shapes are identical in both modes, so UI code never changes.
 */
export async function fetchResource<T>(
  endpoint: string,
  loadMock: () => Promise<MockModule>,
): Promise<T> {
  if (!API_BASE_URL) {
    await new Promise((resolve) => setTimeout(resolve, MOCK_LATENCY_MS))
    const module = await loadMock()
    return module.default as T
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw new ApiError(response.status, `Request to ${endpoint} failed`)
  }

  return (await response.json()) as T
}
