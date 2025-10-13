import { NextResponse } from "next/server";

type RouteParams = {
	params: Promise<{ provider: string }>;
};

export async function GET(request: Request, context: RouteParams) {
	const { provider } = await context.params;
	const { searchParams } = new URL(request.url);
	const code = searchParams.get("code");
	const state = searchParams.get("state");

	if (!code) {
		return NextResponse.json(
			{ error: "Authorization code is missing" },
			{ status: 400 },
		);
	}
}
