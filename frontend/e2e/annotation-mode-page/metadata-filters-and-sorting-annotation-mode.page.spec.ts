import { test, expect } from "@playwright/test";
import {
  newDatasetsMocked,
  mockAllDatasets,
  loginUserAndWaitFor,
  mockRecord,
} from "../common";
import {
  metadataPropertiesCompleted,
  mockRecordForMetadataFilter,
  mockRecordForMetadataSorting,
} from "../common/metadata-api-mock";

const goToAnnotationPage = async (page) => {
  const dataset = newDatasetsMocked[0];
  await mockAllDatasets(page);
  await mockRecord(page, {
    datasetId: dataset.id,
    workspaceId: dataset.workspace_id,
  });
  await metadataPropertiesCompleted(page, dataset.id);

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(2000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(3000);

  return dataset;
};

test.use({
  viewport: { width: 1600, height: 1400 },
});

test.describe("Annotation page Metadata filters", () => {
  test.describe("MetadataFilters", () => {
    test("See the metadata filters", async ({ page }) => {
      await goToAnnotationPage(page);

      await expect(page).toHaveScreenshot();

      await page
        .locator("span")
        .filter({ hasText: "Metadata" })
        .locator("div")
        .click();

      await expect(page).toHaveScreenshot();
    });

    test("The user can filter  automatically when the user just click over term metadata", async ({
      page,
    }) => {
      const dataset = await goToAnnotationPage(page);
      await mockRecordForMetadataFilter(page, dataset.id);

      await expect(page).toHaveScreenshot();

      await page
        .locator("span")
        .filter({ hasText: "Metadata" })
        .locator("div")
        .click();

      await expect(page).toHaveScreenshot();

      await page.getByRole("button", { name: "correctness-langsmith" }).click();

      await expect(page).toHaveScreenshot();

      await page.locator(".re-checkbox").first().click();

      await page.waitForTimeout(1000);

      await expect(page).toHaveScreenshot();

      await page.locator(".empty-content-right").click();

      await page.waitForTimeout(100);

      await expect(page).toHaveScreenshot();
    });

    test("The user can filter the metadata terms with keyboard", async ({
      page,
    }) => {
      const dataset = await goToAnnotationPage(page);
      await mockRecordForMetadataFilter(page, dataset.id);

      await expect(page).toHaveScreenshot();

      await page
        .locator("span")
        .filter({ hasText: "Metadata" })
        .locator("div")
        .click();

      await expect(page).toHaveScreenshot();

      await page.getByRole("button", { name: "correctness-langsmith" }).click();

      await expect(page).toHaveScreenshot();

      await page.locator("section #searchLabel").click();

      await page.keyboard.insertText("unk");

      await expect(page).toHaveScreenshot();
    });

    test("The user can filter automatically by range with mouse", async ({
      page,
    }) => {
      const dataset = await goToAnnotationPage(page);
      await mockRecordForMetadataFilter(page, dataset.id);

      await expect(page).toHaveScreenshot();

      await page
        .locator("span")
        .filter({ hasText: "Metadata" })
        .locator("div")
        .click();

      await expect(page).toHaveScreenshot();

      await page.getByRole("button", { name: "cpu-user" }).click();

      const sliderTrack = await page.getByRole("slider").nth(1);
      const sliderOffsetWidth = await sliderTrack.evaluate((el) => {
        return el.getBoundingClientRect().width * 0.2;
      });

      await sliderTrack.hover({ force: true, position: { x: 0, y: 0 } });
      await page.mouse.down();
      await sliderTrack.hover({
        force: true,
        position: { x: sliderOffsetWidth, y: 0 },
      });
      await page.mouse.up();

      await expect(page).toHaveScreenshot();
    });

    test("The min value never can be less than prefilled by the backend", async ({
      page,
    }) => {
      const dataset = await goToAnnotationPage(page);
      await mockRecordForMetadataFilter(page, dataset.id);

      await expect(page).toHaveScreenshot();

      await page
        .locator("span")
        .filter({ hasText: "Metadata" })
        .locator("div")
        .click();

      await expect(page).toHaveScreenshot();

      await page.getByRole("button", { name: "cpu-user" }).click();
      await page.getByRole("spinbutton").first().fill("0", { force: true });

      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page
        .getByRole("button", { name: "cpu-user-title" })
        .waitFor({ state: "visible" });

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("MetadataSorting", () => {
    test("See the metadata sorting options", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.getByRole("button", { name: "Sort" }).click();

      await expect(page).toHaveScreenshot();
    });

    test("The user can sort by metadata", async ({ page }) => {
      const dataset = await goToAnnotationPage(page);
      await mockRecordForMetadataSorting(page, dataset.id);

      await page.getByRole("button", { name: "Sort" }).click();

      await page.getByRole("button", { name: "model-name" }).click();

      await expect(page).toHaveScreenshot();

      await page.locator(".empty-content-right").click();

      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot();
    });
  });
});
