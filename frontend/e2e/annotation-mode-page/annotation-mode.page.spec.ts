import { test, expect } from "@playwright/test";
import {
  loginUserAndWaitFor,
  mockAllDatasets,
  newDatasetsMocked,
  mockRecord,
  mockTwoRecords,
  mockDiscardRecord,
  mockSubmitRecord,
  mockRecordForLongAndShortQuestion,
} from "../common";

const goToAnnotationPage = async (page, shortAndLongQuestions = false) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);
  const record = shortAndLongQuestions
    ? await mockRecordForLongAndShortQuestion(page, {
      datasetId: dataset.id,
      workspaceId: dataset.workspace_id,
    })
    : await mockRecord(page, {
      datasetId: dataset.id,
      workspaceId: dataset.workspace_id,
    });

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(2000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(3000);

  return record;
};

const goToAnnotationPageWithTwoRecords = async (page) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);

  const record = await mockTwoRecords(page, {
    datasetId: dataset.id,
    workspaceId: dataset.workspace_id,
  });
  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(2000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(3000);

  return record;
}

test.describe("Annotate page", () => {
  test("go to annotation mode page", async ({ page }) => {
    await goToAnnotationPage(page);

    await expect(page).toHaveScreenshot();
  });

  test("filter by workspaces from annotation page", async ({ page }) => {
    await goToAnnotationPage(page);

    await page.getByRole("link", { name: "argilla" }).click();

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

    await page
      .getByText("Review Rating", { exact: true })
      .scrollIntoViewIfNeeded();

    await expect(page).toHaveScreenshot();

    await page.getByText("Ranking", { exact: true }).scrollIntoViewIfNeeded();

    await expect(page).toHaveScreenshot();
  });

  test("clear all questions and discard the record", async ({ page }) => {
    const record = await goToAnnotationPage(page);
    await mockDiscardRecord(page, record.id);

    await page.getByRole("button", { name: "Clear" }).click();

    await page.getByRole("button", { name: "Discard" }).click();

    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot();
  });

  test("label with just one character", async ({ page }) => {
    await goToAnnotationPage(page, true);

    await expect(page).toHaveScreenshot();
  });

  test.describe("pending record", () => {
    test("form have been modified without submit and user try to go to home page => NO alert", async ({ page }) => {
      await goToAnnotationPage(page);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('link', { name: 'Home' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to go to settings page => NO alert", async ({ page }) => {
      await goToAnnotationPage(page);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Dataset settings' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to refresh from sidebar => NO alert", async ({ page }) => {
      await goToAnnotationPage(page);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Refresh' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to go to next record => NO alert", async ({ page }) => {
      await goToAnnotationPageWithTwoRecords(page);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Next' }).click()
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();
    });
  });
  test.describe("discarded record", () => {
    test("form have been modified without submit and user try to go to home page => NO alert", async ({ page }) => {
      const record = await goToAnnotationPage(page);
      await mockDiscardRecord(page, record.id);

      await page.getByRole("button", { name: "Discard" }).click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('link', { name: 'Home' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to go to settings page => NO alert", async ({ page }) => {
      const record = await goToAnnotationPage(page);
      await mockDiscardRecord(page, record.id);

      await page.getByRole("button", { name: "Discard" }).click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Dataset settings' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to refresh from sidebar => NO alert", async ({ page }) => {
      const record = await goToAnnotationPage(page);
      await mockDiscardRecord(page, record.id);

      await page.getByRole("button", { name: "Discard" }).click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Refresh' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to go to next record => NO alert", async ({ page }) => {
      const record = await goToAnnotationPageWithTwoRecords(page);
      await mockDiscardRecord(page, record.id);

      await page.getByRole("button", { name: "Discard" }).click();
      await page.getByRole('button', { name: 'Prev' }).click()
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Next' }).click()
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();
    });
  });
  test.describe("submitted record", () => {
    test("form have been modified without submit and user try to go to home page => NO alert", async ({ page }) => {
      const record = await goToAnnotationPage(page);
      await mockSubmitRecord(page, record.id);

      await page.getByRole("button", { name: "Submit" }).click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('link', { name: 'Home' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to go to settings page => NO alert", async ({ page }) => {
      const record = await goToAnnotationPage(page);
      await mockSubmitRecord(page, record.id);

      await page.getByRole("button", { name: "Submit" }).click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Dataset settings' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to refresh from sidebar => NO alert", async ({ page }) => {
      const record = await goToAnnotationPage(page);
      await mockSubmitRecord(page, record.id);

      await page.getByRole("button", { name: "Submit" }).click();
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Refresh' }).click()

      await expect(page).toHaveScreenshot();
    });

    test("form have been modified without submit and user try to go to next record  => SHOW alert", async ({ page }) => {
      const record = await goToAnnotationPageWithTwoRecords(page);
      await mockSubmitRecord(page, record.id);

      await page.getByRole("button", { name: "Submit" }).click();
      await page.getByRole('button', { name: 'Prev' }).click()
      await page.waitForTimeout(2000);

      await expect(page).toHaveScreenshot();

      await page.getByText('Very Positive').first().click();
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Next' }).click()
      await expect(page).toHaveScreenshot();

      await page.getByRole('alert').locator('span').click(); //close toast and stay on the same record
      await expect(page).toHaveScreenshot();

      await page.getByRole('button', { name: 'Next' }).click()
      await expect(page).toHaveScreenshot();
      
      await page.getByRole('button', { name: 'Ignore and continue' }).click()
      await expect(page).toHaveScreenshot();
    });
  });

});
