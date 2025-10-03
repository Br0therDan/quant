import { defineConfig } from "@hey-api/openapi-ts";

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
			methodNameBuilder: (operation: { id: string | null; }) => {

				const id = operation.id ?? "defaultId";
				return id.charAt(0).toLowerCase() + id.slice(1);
			},
		},
		{
			name: "@hey-api/schemas",
			type: "json",
			exportFromIndex: true,
			nameBuilder: "{{name}}",
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
			mutationOptions: true,
			queryOptions: true,
			infiniteQueryOptions: true,
		},
	],
});
