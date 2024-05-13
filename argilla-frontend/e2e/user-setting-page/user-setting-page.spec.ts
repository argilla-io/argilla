import { test, expect } from "@playwright/test";
import { loginUserAndWaitFor } from "../common";

test.use({
  viewport: { width: 1280, height: 890 },
});

test.describe("User setting page", () => {
  test("see user setting page correctly", async ({ page }) => {
    await loginUserAndWaitFor(page, "datasets");

    await page.getByText("FA", { exact: true }).click();
    await page.getByRole("link", { name: "My settings" }).click();

    await expect(page).toHaveScreenshot();
  });

  test("go to home from user setting page", async ({ page }) => {
    await loginUserAndWaitFor(page, "datasets");

    await page.getByText("FA", { exact: true }).click();
    await page.getByRole("link", { name: "My settings" }).click();

    await page.getByRole("main").getByRole("link", { name: "Home" }).click();

    await page.waitForURL("**/datasets");
  });
});
