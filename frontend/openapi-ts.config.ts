import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
	input: "./src/openapi.json",
	output: {
		format: "prettier",
		path: "./src/client",
	},
	plugins: [
		{
			dates: true,
			name: "@hey-api/transformers",
		},
		{
			asClass: true,
			name: "@hey-api/sdk",
		},
		{
			name: "@hey-api/client-next",
			exportFromIndex: true,
			runtimeConfigPath: "../runtimeConfig",
		},
		{
			name: "@tanstack/react-query",
			exportFromIndex: true,
			queryKeys: true,
			infiniteQueryKeys: {
				tags: true,
			},
			infiniteQueryOptions: {
				meta: (operation) => ({ id: operation.id }),
			},
			mutationOptions: {
				meta: (operation) => ({ id: operation.id }),
			},
		},
	],
});
