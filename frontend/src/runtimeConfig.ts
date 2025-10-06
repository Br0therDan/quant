import type { CreateClientConfig } from "./client";

export const createClientConfig: CreateClientConfig = (config) => ({
	...config,
	baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8500",
	credentials: 'include',
});
