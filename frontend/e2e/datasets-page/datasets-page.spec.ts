import { test, expect } from "@playwright/test";
import {
  loginUserAndWaitFor,
  mockAllDatasets,
  mockWithEmptyDatasets,
} from "../common";
test.describe("Datasets page with datasets", () => {
  test("login successful with correct credentials and get redirect", async ({
    page,
  }) => {
    await loginUserAndWaitFor(page, "datasets");
  });

  test("show datasets table", async ({ page }) => {
    await mockAllDatasets(page);

    await loginUserAndWaitFor(page, "datasets");

    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot();
  });
});

test.describe("Datasets page with no datasets", () => {
  test("show documentation starter first tab", async ({ page }) => {
    await mockWithEmptyDatasets(page);

    await loginUserAndWaitFor(page, "datasets");

    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot();
  });

  test("show documentation starter second tab", async ({ page }) => {
    await mockWithEmptyDatasets(page);

    await loginUserAndWaitFor(page, "datasets");

    await page.getByRole("button", { name: "Other datasets" }).click();

    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot();
  });
});
