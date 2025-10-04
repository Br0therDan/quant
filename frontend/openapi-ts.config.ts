import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({

	input: "./src/openapi.json",
	output: {
		format: "prettier",
		path: "./src/client",
	},
	plugins: [
		"@hey-api/schemas",
		// {
		// 	name: "@hey-api/client-axios",
		// 	exportFromIndex: true,
		// 	runtimeConfigPath: "../runtimeConfig",
		// },
		{
			name: '@hey-api/transformers',
		},
		{
			name: "@hey-api/sdk",
			// NOTE: this doesn't allow tree-shaking
			asClass: true,
			// transformer: true,
			classNameBuilder: "{{name}}Service",
			methodNameBuilder: (operation) => {
				let name = operation.summary;
				if (name) {
					name = name.toLowerCase()
					.replace(/[\s\-_]+(\w)/g, (_, c) => c.toUpperCase())
					.replace(/[\s\-_]+/g, "");
				}
				return name || "defaultMethodName";
			},
		},
		// {
		// 	name: "@hey-api/schemas",
		// 	nameBuilder: (schema) => {
		// 		const splitPascal = (s:string) => s.match(/([A-Z]+(?=[A-Z][a-z])|[A-Z][a-z0-9]*)/g) ?? [s];
		// 		const dropFirstWord = (s:string) => {
		// 			const parts = splitPascal(s);
		// 			return parts.slice(1).join('');
		// 			};
		// 		return dropFirstWord(schema);
		// 	}
		// },
		// {
		// 	name: "@hey-api/client-next",
		// 	exportFromIndex: true,
		// 	runtimeConfigPath: "../runtimeConfig",
		// },
		// {
		// 	name: "@tanstack/react-query",
		// 	exportFromIndex: true,
		// 	queryKeys: true,
		// 	mutationOptions: true,
		// 	queryOptions: true,
		// 	infiniteQueryOptions: true,
		// },
	],
});
