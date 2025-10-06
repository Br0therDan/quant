import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({

	input: "./src/openapi.json",
	output: {
		format: "prettier",
		path: "./src/client",
	},
	plugins: [
		"@hey-api/schemas",
		{
			name: "@hey-api/client-next",
			exportFromIndex: true,
			runtimeConfigPath: "../runtimeConfig",
		},
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
		{
			name: "@tanstack/react-query",
			exportFromIndex: true,
		},
	],
});
