import { Page } from "@playwright/test";
export interface DatasetData {
  datasetId: string;
  workspaceId: string;
}

const oldDatasets = [
  {
    tags: {},
    metadata: {},
    name: "span_marker_conll_8_epochs_corr_annot",
    task: "TokenClassification",
    workspace: "argilla",
    id: "argilla.span_marker_conll_8_epochs_corr_annot",
    owner: "argilla",
    created_at: "2023-05-12T13:51:03.944415",
    created_by: "argilla",
    last_updated: "2023-05-12T13:51:34.749372",
  },
  {
    tags: {
      description:
        "This dataset contains text2text records with 10 predictions",
    },
    metadata: {},
    name: "text2text-10-predictions",
    task: "Text2Text",
    workspace: "recognai",
    id: "recognai.text2text-10-predictions",
    owner: "recognai",
    created_at: "2023-02-24T12:02:42.893649",
    created_by: "recognai",
    last_updated: "2023-05-17T13:29:18.547746",
  },
  {
    tags: {},
    metadata: {},
    name: "settings_textclass_with_labels",
    task: "TextClassification",
    workspace: "recognai",
    id: "recognai.settings_textclass_with_labels",
    owner: "recognai",
    created_at: "2023-03-06T19:09:13.471856",
    created_by: "recognai",
    last_updated: "2023-03-07T15:33:46.194890",
  },
];

export const newDatasetsMocked = [
  {
    id: "ff0046f3-5098-40e6-80e1-58945faa185c",
    name: "feedback-dataset-1",
    guidelines:
      "This dataset collects human feedback on replies generated by an LLM. It is based on prompts and responses from the Open Assistant dataset.\nQuestion 1: Select your preferred reply\nSelect which reply you like best. Click 1 for reply_1, click 2 for reply_2.\nQuestion 2: Rate the overall quality of reply no.1\nCheck if reply_1 has typos or errors and select your score, 1 being very bad and 5 being very good.\nQuestion 3: Rate the helpfulness of reply no.1\nCheck if reply_1 is clear and offers a real solution to the prompt and select your score from 1 to 5, where 1 is not helpful and 5 very helpful. \nQuestion 4: Rate the harmlessness of reply no.1\nCheck if reply_1 has any content that could be considered offensive, violent or dangerous. Then select your score, 1 being very harmful and 5 being harmless.\nQuestion 5: Propose a correction for reply no.1 (optional)\nIf needed, provide a corrected or alternative text for reply_1\nQuestion 6: Rate the overall quality of reply no.2\nCheck if reply_2 has typos or errors and select your score, 1 being very bad and 5 being very good.\nQuestion 7: Rate the helpfulness of reply no.2\nCheck if reply_2 is clear and offers a real solution to the prompt and select your score from 1 to 5, where 1 is not helpful and 5 very helpful. \nQuestion 8: Rate the harmlessness of reply no.2\nCheck if reply_2 has any content that could be considered offensive, violent or dangerous. Then select your score, 1 being very harmful and 5 being harmless.\nQuestion 9: Propose a correction for reply no.2 (optional)\nIf needed, provide a corrected or alternative text for reply_2\nQuestion 10: Comments (optional)\nLeave any comments you may have about this record",
    status: "ready",
    workspace_id: "4e70e21a-7533-41e9-8a25-11d6ee3091be",
    inserted_at: "2023-05-10T09:23:35.343928",
    updated_at: "2023-05-10T09:23:39.615994",
  },
  {
    id: "25073901-a24d-4416-b331-71a497b38063",
    name: "feedback-dataset-2",
    guidelines:
      "This dataset collects human feedback on replies generated by an LLM. It is based on prompts and responses from the Open Assistant dataset.\nQuestion 1: Select your preferred reply\nSelect which reply you like best. Click 1 for reply_1, click 2 for reply_2.\nQuestion 2: Rate the overall quality of reply no.1\nCheck if reply_1 has typos or errors and select your score, 1 being very bad and 5 being very good.\nQuestion 3: Rate the helpfulness of reply no.1\nCheck if reply_1 is clear and offers a real solution to the prompt and select your score from 1 to 5, where 1 is not helpful and 5 very helpful. \nQuestion 4: Rate the harmlessness of reply no.1\nCheck if reply_1 has any content that could be considered offensive, violent or dangerous. Then select your score, 1 being very harmful and 5 being harmless.\nQuestion 5: Propose a correction for reply no.1 (optional)\nIf needed, provide a corrected or alternative text for reply_1\nQuestion 6: Rate the overall quality of reply no.2\nCheck if reply_2 has typos or errors and select your score, 1 being very bad and 5 being very good.\nQuestion 7: Rate the helpfulness of reply no.2\nCheck if reply_2 is clear and offers a real solution to the prompt and select your score from 1 to 5, where 1 is not helpful and 5 very helpful. \nQuestion 8: Rate the harmlessness of reply no.2\nCheck if reply_2 has any content that could be considered offensive, violent or dangerous. Then select your score, 1 being very harmful and 5 being harmless.\nQuestion 9: Propose a correction for reply no.2 (optional)\nIf needed, provide a corrected or alternative text for reply_2\nQuestion 10: Comments (optional)\nLeave any comments you may have about this record",
    status: "ready",
    workspace_id: "4e70e21a-7533-41e9-8a25-11d6ee3091be",
    inserted_at: "2023-05-10T11:55:23.354714",
    updated_at: "2023-05-10T11:55:27.599602",
  },
  {
    id: "25073901-a24d-4416-b331-71a497b38063",
    name: "feedback-dataset-3",
    guidelines:
      "This dataset collects human feedback on replies generated by an LLM. It is based on prompts and responses from the Open Assistant dataset.\nQuestion 1: Select your preferred reply\nSelect which reply you like best. Click 1 for reply_1, click 2 for reply_2.\nQuestion 2: Rate the overall quality of reply no.1\nCheck if reply_1 has typos or errors and select your score, 1 being very bad and 5 being very good.\nQuestion 3: Rate the helpfulness of reply no.1\nCheck if reply_1 is clear and offers a real solution to the prompt and select your score from 1 to 5, where 1 is not helpful and 5 very helpful. \nQuestion 4: Rate the harmlessness of reply no.1\nCheck if reply_1 has any content that could be considered offensive, violent or dangerous. Then select your score, 1 being very harmful and 5 being harmless.\nQuestion 5: Propose a correction for reply no.1 (optional)\nIf needed, provide a corrected or alternative text for reply_1\nQuestion 6: Rate the overall quality of reply no.2\nCheck if reply_2 has typos or errors and select your score, 1 being very bad and 5 being very good.\nQuestion 7: Rate the helpfulness of reply no.2\nCheck if reply_2 is clear and offers a real solution to the prompt and select your score from 1 to 5, where 1 is not helpful and 5 very helpful. \nQuestion 8: Rate the harmlessness of reply no.2\nCheck if reply_2 has any content that could be considered offensive, violent or dangerous. Then select your score, 1 being very harmful and 5 being harmless.\nQuestion 9: Propose a correction for reply no.2 (optional)\nIf needed, provide a corrected or alternative text for reply_2\nQuestion 10: Comments (optional)\nLeave any comments you may have about this record",
    status: "ready",
    workspace_id: "4e70e21a-7533-41e9-8a25-11d6ee3091bd",
    inserted_at: "2023-05-10T11:55:23.354714",
    updated_at: "2023-05-10T11:55:27.599602",
  },
];

export const workspacesMocked = [
  {
    id: "4e70e21a-7533-41e9-8a25-11d6ee3091be",
    name: "argilla",
    inserted_at: "2023-04-27T15:38:56.032436",
    updated_at: "2023-04-27T15:38:56.032436",
  },
  {
    id: "9c14ca14-65bb-4c27-ba1f-cf7e4a6398e8",
    name: "recognai",
    inserted_at: "2023-04-27T15:44:23.423662",
    updated_at: "2023-04-27T15:44:23.423662",
  },
  {
    id: "4e70e21a-7533-41e9-8a25-11d6ee3091bd",
    name: "other-argilla",
    inserted_at: "2023-04-27T15:44:23.423662",
    updated_at: "2023-04-27T15:44:23.423662",
  },
];

export const mockWithEmptyDatasets = async (page: Page) => {
  await page.route("*/**/api/datasets/", async (route) => {
    await route.fulfill({ json: [] });
  });
  await page.route("*/**/api/v1/me/datasets", async (route) => {
    await route.fulfill({ json: { items: [] } });
  });
};

export const mockAllDatasets = async (page: Page) => {
  await page.route("*/**/api/datasets/", async (route) => {
    await route.fulfill({ json: oldDatasets });
  });
  await page.route("*/**/api/v1/me/datasets", async (route) => {
    await route.fulfill({ json: { items: newDatasetsMocked } });
  });
  await page.route("*/**/api/workspaces", async (route) => {
    await route.fulfill({ json: workspacesMocked });
  });
};

export const mockFeedbackTaskDataset = async (
  page: Page,
  { datasetId, workspaceId }: DatasetData
) => {
  await page.route(`*/**/api/v1/datasets/${datasetId}`, async (route) => {
    await route.fulfill({
      json: newDatasetsMocked.find((d) => d.id === datasetId),
    });
  });

  await page.route(`*/**/api/v1/workspaces/${workspaceId}`, async (route) => {
    await route.fulfill({
      json: workspacesMocked.find((w) => w.id === workspaceId),
    });
  });

  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/metrics`,
    async (route) => {
      await route.fulfill({
        json: {
          records: {
            count: 1000,
          },
          responses: {
            count: 29,
            submitted: 25,
            discarded: 4,
            draft: 0,
          },
        },
      });
    }
  );
};
