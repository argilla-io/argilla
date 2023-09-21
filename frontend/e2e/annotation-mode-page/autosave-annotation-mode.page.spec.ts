import { test, expect } from "@playwright/test";
import {
  newDatasetsMocked,
  mockAllDatasets,
  mockTwoRecords,
  loginUserAndWaitFor,
  mockDraftRecord,
  mockRecordResponses,
} from "../common";

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
};

test.use({
  viewport: { width: 1600, height: 1400 },
});

test.describe("pending record", () => {
  test("form have been modified without submit and user try to go to home page => NO alert", async ({
    page,
  }) => {
    await goToAnnotationPageWithTwoRecords(page);
    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("link", { name: "Home" }).click();

    await expect(page).toHaveScreenshot();
  });

  test("form have been modified without submit and user try to go to settings page => NO alert", async ({
    page,
  }) => {
    await goToAnnotationPageWithTwoRecords(page);

    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();
    await expect(page).toHaveScreenshot();

    await page.locator(".icon-with-badge").first().click();

    await expect(page).toHaveScreenshot();
  });

  test("form have been modified without submit and user try to refresh from sidebar => NO alert", async ({
    page,
  }) => {
    await goToAnnotationPageWithTwoRecords(page);

    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();
    await expect(page).toHaveScreenshot();

    await page.locator("span:nth-child(2) > .icon-button").click();
    await page.waitForTimeout(200);

    await expect(page).toHaveScreenshot();
  });

  test("form have been modified without submit and user try to go to next record => NO alert", async ({
    page,
  }) => {
    await goToAnnotationPageWithTwoRecords(page);

    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Next" }).click();
    await page.waitForTimeout(200);

    await expect(page).toHaveScreenshot();
  });

  test("when the user modifies something after 3 seconds we can see the saved label", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockDraftRecord(page, record.id);
    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();

    await page.getByText("Saving").waitFor({ state: "visible" });
    await expect(page).toHaveScreenshot();

    await page.getByText("Saved").waitFor({ state: "visible" });

    await expect(page).toHaveScreenshot();
  });

  test("when the record is saving as a draft the user can not close the page", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockDraftRecord(page, record.id);

    await page.getByText("Very Positive").first().click();

    await page.getByText("Saving").waitFor({ state: "visible" });

    page.on("dialog", (dialog) => {
      expect(dialog.type()).toBe("beforeunload");
    });

    await page.close({ runBeforeUnload: true });
  });

  test("user submit and then goes back to previous record, show updated answers", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "submitted");
    await page.getByText("Very Positive").first().click();
    await page.getByText('Positive').nth(3).click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Submit" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();
  });
});
test.describe("discarded record", () => {
  test("when the user modifies a discarded record after 2 seconds should be pending", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "discarded");
    await page.getByRole("button", { name: "Discard" }).click();
    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();
    await mockDraftRecord(page, record.id);

    await page.getByText("Very Positive").first().click();

    await page.getByText("Saving").waitFor({ state: "visible" });
    await expect(page).toHaveScreenshot();

    await page.getByText("Saved").waitFor({ state: "visible" });

    await expect(page).toHaveScreenshot();
  });
});
test.describe("submitted record", () => {
  test("the user can not see the toaster if he modified a submitted record and go to home", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "submitted");
    await page.getByRole("button", { name: "Submit" }).click();
    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("link", { name: "Home" }).click();

    await expect(page).toHaveScreenshot();
  });

  test("the user can not see the toaster if he modified a submitted record and go to settings page", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "submitted");
    await page.getByRole("button", { name: "Submit" }).click();
    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();
    await expect(page).toHaveScreenshot();

    await page.locator(".icon-with-badge").first().click();
    await expect(page).toHaveScreenshot();
  });

  test("the user can not see the toaster if he modified a submitted record and refresh the page", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "submitted");
    await page.getByRole("button", { name: "Submit" }).click();
    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();
    await expect(page).toHaveScreenshot();

    await page.locator("span:nth-child(2) > .icon-button").click();

    await expect(page).toHaveScreenshot();
  });

  test("the user can see the toaster if he modified a submitted record and go to next record", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "submitted");
    await page.getByRole("button", { name: "Submit" }).click();
    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Next" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("alert").locator("span").click(); //close toast and stay on the same record
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Next" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Ignore and continue" }).click();
    await expect(page).toHaveScreenshot();
  });

  test("when the user try to search something when is in a changed submitted record see the toaster", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "submitted");
    await page.getByRole("button", { name: "Submit" }).click();
    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();

    await page
      .getByPlaceholder("Introduce a query")
      .fill("Try to find other record");
    await expect(page).toHaveScreenshot();

    await page.keyboard.press("Enter");

    await page
      .getByText("You didn't submit your changes")
      .waitFor({ state: "visible" });
    await expect(page).toHaveScreenshot();
  });

  test("when the user try to filter by status and he modified previously the submitted record see the toaster", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "submitted");
    await page.getByRole("button", { name: "Submit" }).click();
    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByText("Very Positive").first().click();

    await page.getByRole("button", { name: "Pending" }).click();
    await page.waitForTimeout(100);
    await page.getByText("Discarded").click();

    await page
      .getByText("You didn't submit your changes")
      .waitFor({ state: "visible" });
    await expect(page).toHaveScreenshot();
  });

  test("when user ignore current modification and go back to same record, the record have the initial answers", async ({
    page,
  }) => {
    const record = await goToAnnotationPageWithTwoRecords(page);
    await mockRecordResponses(page, record.id, "submitted");
    await page.getByText("Very Positive").first().click();
    await page.getByText('Positive').nth(3).click();
    await page.getByRole("button", { name: "Submit" }).click();
    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();


    await page.getByText('Negative').nth(1).click();
    await page.getByText('Disappointed').nth(1).click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Next" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Ignore and continue" }).click();
    await expect(page).toHaveScreenshot();

    await page.getByRole("button", { name: "Prev" }).click();
    await expect(page).toHaveScreenshot();
  });
});
