import { NextResponse, type NextRequest } from "next/server";
import { AuthService } from "@/client";
import { cookies } from "next/headers";

export async function POST(request: NextRequest) {
	try {
		const body = await request.json();
		const { username, password } = body;

		if (!username || !password) {
			return NextResponse.json(
				{ error: "Username and password are required" },
				{ status: 400 },
			);
		}

		const response = await AuthService.login({
			body: { username, password },
		});

		if (response.error) {
			return NextResponse.json(
				{ error: response.error.detail || "Login failed" },
				{ status: 401 },
			);
		}
		const cookieStore = await cookies();
		const accessToken = response.data?.access_token ?? undefined;
		const refreshToken = response.data?.refresh_token ?? undefined;

		cookieStore.set("access_token", accessToken || "", {
			httpOnly: true,
			secure: process.env.NODE_ENV === "production",
			sameSite: "lax",
		});
		cookieStore.set("refresh_token", refreshToken || "", {
			httpOnly: true,
			secure: process.env.NODE_ENV === "production",
			sameSite: "lax",
		});
		cookieStore.set(
			"user_info",
			JSON.stringify(response.data?.user_info) || "",
			{
				httpOnly: false,
				secure: process.env.NODE_ENV === "production",
				sameSite: "lax",
			},
		);

		return NextResponse.json({ message: "Login successful" }, { status: 200 });
	} catch (error) {
		console.error("Login API error:", error);
		return NextResponse.json(
			{ error: "An unexpected error occurred" },
			{ status: 500 },
		);
	}
}
