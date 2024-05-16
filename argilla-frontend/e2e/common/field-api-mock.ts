import { Page } from "@playwright/test";

const fieldOne = {
  id: "4214d164-5edd-496a-be04-a4babc9d74ed",
  name: "text",
  title: "Text",
  required: true,
  settings: {
    type: "text",
    use_markdown: false,
  },
  inserted_at: "2023-07-18T07:43:35",
  updated_at: "2023-07-18T07:43:35",
};

export const mockFields = async (page: Page, datasetId: string) => {
  await page.route(
    `*/**/api/v1/datasets/${datasetId}/fields`,
    async (route) => {
      await route.fulfill({
        json: {
          items: [fieldOne],
        },
      });
    }
  );
};
