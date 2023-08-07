import { test, expect, Page } from "@playwright/test";
import {
  mockAllDatasets,
  loginUserAndWaitFor,
  newDatasetsMocked,
  mockRecord,
} from "../common";

test.use({
  viewport: { width: 1600, height: 1800 },
});

const goToDatasetSettingPage = async (page: Page) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);
  const record = await mockRecord(page, {
    datasetId: dataset.id,
    workspaceId: dataset.workspace_id,
  });

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(1000);

  await page
    .locator("li")
    .filter({
      hasText: dataset.name,
    })
    .getByTitle("Go to dataset settings")
    .click();

  await page.waitForTimeout(1000);

  return record;
};

test.describe("Dataset setting page", () => {
  test("information tab", async ({ page }) => {
    await goToDatasetSettingPage(page);

    await expect(page).toHaveScreenshot();
  });

  test("fields tab", async ({ page }) => {
    await goToDatasetSettingPage(page);

    await page.getByRole("button", { name: "Fields" }).click();

    await expect(page).toHaveScreenshot();
  });

  test.describe("questions tab", () => {
    test.describe("Single label", () => {
      test("change question title", async ({ page }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await page
          .locator("#title-045c18d5-57b6-408a-8db3-bc11b9f54541")
          .fill("Changed");

        await expect(page).toHaveScreenshot();
      });

      test("show required error when the title is empty", async ({ page }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await page
          .locator("#title-045c18d5-57b6-408a-8db3-bc11b9f54541")
          .fill("");

        await expect(page).toHaveScreenshot();
      });

      test("show error when the title is bigger than 200 characters", async ({
        page,
      }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await page
          .locator("#title-045c18d5-57b6-408a-8db3-bc11b9f54541")
          .fill(Array(201).fill("X").join(""));

        await expect(page).toHaveScreenshot();
      });

      test("change question description", async ({ page }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await page
          .locator("#description-045c18d5-57b6-408a-8db3-bc11b9f54541")
          .fill("Changed description");

        await expect(page).toHaveScreenshot();
      });

      test("show error when the description is bigger than 500 characters", async ({
        page,
      }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await page
          .locator("#description-045c18d5-57b6-408a-8db3-bc11b9f54541")
          .fill(Array(501).fill("X").join(""));

        await expect(page).toHaveScreenshot();
      });

      test("change question visible options", async ({ page }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await expect(page).toHaveScreenshot();

        await page.getByRole("slider").first().click();

        await page.mouse.down();
        await page.mouse.move(4, 0);

        await expect(page).toHaveScreenshot();
      });
    });

    test.describe("Text component", () => {
      test("change question title", async ({ page }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await page
          .locator("#title-7a642861-5c68-418e-8e9f-3fb95d837b86")
          .fill("Changed");

        await expect(page).toHaveScreenshot();
      });

      test("change question description", async ({ page }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await page
          .locator("#description-7a642861-5c68-418e-8e9f-3fb95d837b86")
          .fill("Changed description");

        await expect(page).toHaveScreenshot();
      });

      test("change question use markdown", async ({ page }) => {
        await goToDatasetSettingPage(page);

        await page.getByRole("button", { name: "Questions" }).click();

        await page.waitForTimeout(200);

        await page
          .locator("#contentId")
          .fill('```js\nconsole.log("Hi 👋")\n```');

        await expect(page).toHaveScreenshot();

        await page
          .locator("form")
          .filter({
            hasText:
              "review-review text Title Description Use Markdown Cancel Update",
          })
          .getByRole("button")
          .first()
          .click();

        await expect(page).toHaveScreenshot();
      });
    });
  });
});
