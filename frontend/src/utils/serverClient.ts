import { client } from "@/client/client.gen";
import { cookies } from "next/headers";

export async function createServerClient() {
	const cookieStore = await cookies();
	const token = cookieStore.get("access_token")?.value;

	client.setConfig({
		auth: token,
	});

	return client;
}
