import { Page } from "@playwright/test";
import {
  loginUserAndWaitFor,
  mockAllDatasets,
  newDatasetsMocked,
  mockRecord,
  mockRecordWith12Ranking,
  mockRecordWithRating,
  mockRecordForLongAndShortQuestion,
} from "../common";

export const goToAnnotationPage = async (
  page,
  shortAndLongQuestions = false
) => {
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

export const goToAnnotationPageWith12Ranking = async (page: Page) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);
  await mockRecordWith12Ranking(page, {
    datasetId: dataset.id,
    workspaceId: dataset.workspace_id,
  });

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(1000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(1000);
};
export const goToAnnotationPageWith10Rating = async (page) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);
  await mockRecordWithRating(page, {
    datasetId: dataset.id,
    workspaceId: dataset.workspace_id,
  });

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(2000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(3000);
};
