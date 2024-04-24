import { test, expect } from "@playwright/test";
import { loginUserAndWaitFor } from "../common";

test.describe("Login page", () => {
  test("has title", async ({ page }) => {
    await page.goto("/");

    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot();
  });

  test("login successful with correct credentials", async ({ page }) => {
    await loginUserAndWaitFor(page, "datasets");
  });
});
