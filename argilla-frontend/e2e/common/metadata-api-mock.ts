import { recordTwo } from "./record-api-mock";

const metadataFromBackend = {
  items: [
    {
      id: "acb07ca1-aba8-48c3-b52e-f3a227808dfb",
      name: "correctness-langsmith",
      title: "correctness-langsmith-title",
      settings: {
        type: "terms",
        values: ["incorrect", "unknown", "correct"],
      },
    },
    {
      id: "cc35ee5b-2a88-4350-b536-be5088aa490e",
      name: "model-name",
      title: "model-name-title",
      settings: {
        type: "terms",
        values: [
          "gpt3.5-turbo-instruct",
          "gpt4",
          "bard",
          "gpt3.5-turbo",
          "claude",
          "llama2-7B",
        ],
      },
    },
    {
      id: "daf89c99-f7a5-49ce-a9a3-0f04b458acf0",
      name: "temperature",
      title: "temperature-title",
      settings: {
        type: "float",
        min: 0.0,
        max: 0.99,
      },
    },
    {
      id: "cfea0213-4c90-4006-afeb-5a94cebc94cd",
      name: "cpu-user",
      title: "cpu-user-title",
      settings: {
        type: "float",
        min: 1.06,
        max: 9.88,
      },
    },
    {
      id: "06e04754-a445-4cf9-bbd4-0a7fa1fef559",
      name: "cpu-system",
      title: "cpu-system-title",
      settings: {
        type: "float",
        min: 0.52,
        max: 4.99,
      },
    },
    {
      id: "1cc9a1eb-618b-4dd1-8637-ed11d7e7f04c",
      name: "library-version",
      title: "library-version-title",
      settings: {
        type: "terms",
        values: ["0.0.301"],
      },
    },
  ],
};

const recordsMatchingMetadata = {
  items: [recordTwo],
  total: 117,
};

export const metadataPropertiesCompleted = async (page, datasetId) => {
  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/metadata-properties`,
    async (route) => {
      await route.fulfill({
        json: metadataFromBackend,
      });
    }
  );
};

export const mockRecordForMetadataFilter = async (page, datasetId) => {
  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/records?include=responses&include=suggestions&offset=0&limit=10&response_status=pending&response_status=draft&metadata=correctness-langsmith%3Aincorrect`,
    async (route) => {
      await route.fulfill({
        json: recordsMatchingMetadata,
      });
    }
  );
};

export const mockRecordForMetadataSorting = async (page, datasetId) => {
  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/records?include=responses&include=suggestions&offset=0&limit=10&response_status=pending&response_status=draft&sort_by=metadata.model-name%3Aasc`,
    async (route) => {
      await route.fulfill({
        json: recordsMatchingMetadata,
      });
    }
  );
};
