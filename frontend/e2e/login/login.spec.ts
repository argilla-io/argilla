import { test, expect } from "@playwright/test";

test.describe("Login page", () => {
	test("has title", async ({ page }) => {
		await page.goto("/");

		await expect(page).toHaveTitle("Argilla");
	});

	test("login successful with correct credentials", async ({ page }) => {
		await page.goto("/login");
		await page.getByPlaceholder("Enter your username").click();

		await page.getByPlaceholder("Enter your username").fill("admin");

		await page.getByPlaceholder("Enter your password").fill("12345678");

		await page.getByRole("button", { name: "Enter" }).click();

		await page.waitForURL("**/datasets");
	});
});
