import { test, expect } from "@playwright/test";
import {
  loginUserAndWaitFor,
  mockAllDatasets,
  newDatasetsMocked,
  mockRecord,
} from "../common";

const goToAnnotationPage = async (page) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);
  await mockRecord(page, {
    datasetId: dataset.id,
    workspaceId: dataset.workspace_id,
  });

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(2000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(3000);
};

test.describe("Annotate page", () => {
  test("go to annotation mode page", async ({ page }) => {
    await goToAnnotationPage(page);

    await expect(page).toHaveScreenshot();
  });

  test("hide spark icon when user change suggested answer", async ({
    page,
  }) => {
    await goToAnnotationPage(page);

    await page.getByText("Very Positive").first().click();

    await expect(page).toHaveScreenshot();
  });

  test("show spark icon when user change suggested answer and go back to default", async ({
    page,
  }) => {
    await goToAnnotationPage(page);

    await page.getByText("Positive").first().click();

    await expect(page).toHaveScreenshot();
  });

  test("disable submit when user no complete required answer", async ({
    page,
  }) => {
    await goToAnnotationPage(page);

    await page.getByText("Positive").nth(1).click();

    await expect(page).toHaveScreenshot();
  });

  test("disable submit when user complete partially ranking question", async ({
    page,
  }) => {
    await goToAnnotationPage(page);

    await page
      .getByTitle("Option A")
      .dragTo(page.locator(".draggable__questions-container"));

    await expect(page).toHaveScreenshot();
  });

  test("clear all questions", async ({ page }) => {
    await goToAnnotationPage(page);

    await page.getByRole("button", { name: "Clear" }).click();

    await expect(page).toHaveScreenshot();

    await page.getByText("Review Rating (optional)").scrollIntoViewIfNeeded();

    await expect(page).toHaveScreenshot();

    await page.getByText("Ranking (optional)").scrollIntoViewIfNeeded();

    await expect(page).toHaveScreenshot();
  });
});
