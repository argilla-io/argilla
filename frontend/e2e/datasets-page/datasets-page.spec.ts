import { test, expect } from "@playwright/test";
import { loginUserAndWaitFor } from "../common";

test.describe("Datasets page with datasets", () => {
  test("login successful with correct credentials and get redirect", async ({
    page,
  }) => {
    await loginUserAndWaitFor(page, "datasets");
  });
});

test.describe("Datasets page with no datasets", () => {
  test("show documentation starter first tab", async ({ page }) => {
    await page.route("*/**/api/datasets/", async (route) => {
      await route.fulfill({ json: [] });
    });
    await page.route("*/**/api/v1/me/datasets", async (route) => {
      await route.fulfill({ json: { items: [] } });
    });

    await loginUserAndWaitFor(page, "datasets");

    await expect(page).toHaveScreenshot();
  });

  test("show documentation starter second tab", async ({ page }) => {
    await page.route("*/**/api/datasets/", async (route) => {
      await route.fulfill({ json: [] });
    });
    await page.route("*/**/api/v1/me/datasets", async (route) => {
      await route.fulfill({ json: { items: [] } });
    });

    await loginUserAndWaitFor(page, "datasets");

    await page.waitForLoadState("domcontentloaded");

    await page.getByRole("button", { name: "Other datasets" }).click();

    await expect(page).toHaveScreenshot();
  });
});
