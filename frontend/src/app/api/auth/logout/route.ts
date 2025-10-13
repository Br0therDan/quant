import { NextResponse } from "next/server";
import { AuthService } from "@/client";
import { cookies } from "next/headers";

export async function GET() {
	try {
		const response = await AuthService.logout();
		if (response.error) {
			return NextResponse.json(
				{ error: response.error || "Logout failed" },
				{ status: 400 },
			);
		}
		const cookieStore = await cookies();
		cookieStore.delete("access_token");
		cookieStore.delete("refresh_token");
		cookieStore.delete("user_info");

		return NextResponse.json({ message: "Logout successful" }, { status: 200 });
	} catch (error) {
		console.error("Logout API error:", error);
		return NextResponse.json(
			{ error: "An unexpected error occurred" },
			{ status: 500 },
		);
	}
}
