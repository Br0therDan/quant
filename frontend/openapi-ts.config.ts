import { defineConfig } from "@hey-api/openapi-ts";
import { mutationOptions } from '@tanstack/react-query';

export default defineConfig({
	input: "./src/openapi.json",
	output: {
		format: "prettier",
		path: "./src/client",
	},
	plugins: [
		{
			name: "@hey-api/sdk",
			// NOTE: this doesn't allow tree-shaking
			asClass: true,
			operationId: true,
			classNameBuilder: "{{name}}Service",
			methodNameBuilder: (operation: { id: string; }) => {

				const id: string = operation.id
				return id.charAt(0).toLowerCase() + id.slice(1)
			},
		},
		{
			name: "@hey-api/schemas",
			type: "json",
			namespace: "Schemas",
			exportFromIndex: true,
			// groupByTag: true,
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
			mutationKeys: true,
			// queryOptions: {
			// 	meta: (operation) => ({ id: operation.id }),
			// },
			// infiniteQueryOptions: {
			// 	meta: (operation) => ({ id: operation.id }),
			// },
			// mutationOptions: {
			// 	meta: (operation) => ({ id: operation.id }),
			// },
		},
	],
});
