import { Page } from "@playwright/test";
import { DatasetData, mockFeedbackTaskDataset } from "./dataset-api-mock";
import {
  mockQuestion,
  mockQuestionWith12Ranking,
  mockQuestionWithRating,
  mockQuestionLongAndShortQuestions,
} from "./question-api-mock";
import { mockFields } from "./field-api-mock";
import { useDebounce } from "~/v1/infrastructure/services/useDebounce";

export const recordOne = {
  id: "9cf21756-00a0-479d-aa46-f2ef9dcf89f1",
  fields: {
    text: "Some films that you pick up for a pound turn out to be rather good - 23rd Century films released dozens of obscure Italian and American movie that were great, but although Hardgore released some Fulci films amongst others, the bulk of their output is crap like The Zombie Chronicles.<br /><br />The only positive thing I can say about this film is that it's nowhere near as annoying as the Stink of Flesh. Other than that, its a very clumsy anthology film with the technical competence of a Lego house built by a whelk.<br /><br />It's been noted elsewhere, but you really do have to worry about a film that inserts previews of the action into its credit sequence, so by the time it gets to the zombie attacks, you've seen it all already.<br /><br />Bad movie fans will have a ball watching the 18,000 continuity mistakes and the diabolical acting of the cast (especially the hitchhiker, who was so bad he did make me laugh a bit), and kudos to Hardgore for getting in to the spirit of things by releasing a print so bad it felt like I was watching some beat up home video of a camping trip.<br /><br />Awful, awful stuff. We've all made stuff like this when we've gotten a hold of a camera, but common sense prevails and these films languish in our cupboards somewhere. Avoid.",
  },
  metadata: null,
  external_id: null,
  responses: [],
  suggestions: [
    {
      question_id: "045c18d5-57b6-408a-8db3-bc11b9f54541",
      type: null,
      score: null,
      value: "positive",
      agent: null,
      id: "61373cf9-1d26-427b-885e-380ba90a2491",
    },
    {
      question_id: "682dd011-6a8a-452e-8900-483279c6acee",
      type: null,
      score: null,
      value: ["positive", "very_positive"],
      agent: null,
      id: "59f5d5ee-18d0-4fb2-b437-b199d8057b43",
    },
    {
      question_id: "58f80371-7302-4151-abbb-ab180d229f95",
      type: null,
      score: null,
      value: 5,
      agent: null,
      id: "db2aea55-babc-473e-b97c-3db201bc202a",
    },
    {
      question_id: "7a642861-5c68-418e-8e9f-3fb95d837b86",
      type: null,
      score: null,
      value: "This is a review of the review",
      agent: null,
      id: "fc235b88-4833-4013-a5c5-d4d078e3833a",
    },
    {
      question_id: "b42c4d1a-6a87-42c7-bfcb-5e1df333c361",
      type: null,
      score: null,
      value: [
        {
          value: "option-a",
          rank: 1,
        },
        {
          value: "option-d",
          rank: 2,
        },
        {
          value: "option-c",
          rank: 3,
        },
        {
          value: "option-b",
          rank: 4,
        },
      ],
      agent: null,
      id: "2639dec2-f0e4-43d7-a151-288f033f772e",
    },
  ],
  inserted_at: "2023-07-18T07:43:38",
  updated_at: "2023-07-18T07:43:38",
};

export const recordTwo = {
  id: "9cf21756-00a0-479d-aa46-f2ef9dcf89f2",
  fields: {
    text: "Second record",
  },
  metadata: null,
  external_id: null,
  responses: [],
  suggestions: [],
  inserted_at: "2023-07-18T07:43:38",
  updated_at: "2023-07-18T07:43:38",
};

const recordFor12rankingA = {
  id: "1da11112-69ac-4cc9-947e-c8293243510a",
  fields: {
    text: "First Record",
  },
  metadata: {},
  external_id: null,
  responses: [],
  suggestions: [],
  inserted_at: "2023-07-26T12:15:02",
  updated_at: "2023-07-26T12:15:02",
};

const recordFor12rankingB = {
  id: "1da11112-69ac-4cc9-947e-c8293243510b",
  fields: {
    text: "Second record",
  },
  metadata: {},
  external_id: null,
  responses: [],
  suggestions: [],
  inserted_at: "2023-07-26T12:15:02",
  updated_at: "2023-07-26T12:15:02",
};

const recordForRating = {
  id: "0203fc47-e30a-4f97-8f13-12bb816a3059",
  fields: {
    text: "Rate me",
  },
  metadata: {},
  external_id: null,
  responses: [],
  suggestions: [],
  inserted_at: "2023-07-21T09:23:20",
  updated_at: "2023-07-21T09:23:20",
};

export const mockRecord = async (
  page: Page,
  { datasetId, workspaceId }: DatasetData
) => {
  await mockFeedbackTaskDataset(page, { datasetId, workspaceId });

  await mockQuestion(page, datasetId);

  await mockFields(page, datasetId);

  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/records?include=responses&include=suggestions&offset=0&limit=10&response_status=pending&response_status=draft`,
    async (route) => {
      await route.fulfill({
        json: {
          items: [recordOne],
        },
      });
    }
  );

  return recordOne;
};

export const mockTwoRecords = async (
  page: Page,
  { datasetId, workspaceId }: DatasetData
) => {
  await mockFeedbackTaskDataset(page, { datasetId, workspaceId });

  await mockQuestion(page, datasetId);

  await mockFields(page, datasetId);
  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/records?include=responses&include=suggestions&offset=0&limit=10&response_status=pending&response_status=draft`,
    async (route) => {
      await route.fulfill({
        json: {
          items: [recordOne, recordTwo],
        },
      });
    }
  );

  return recordOne;
};

export const mockRecordForLongAndShortQuestion = async (
  page: Page,
  { datasetId, workspaceId }: DatasetData
) => {
  await mockFeedbackTaskDataset(page, { datasetId, workspaceId });

  await mockQuestionLongAndShortQuestions(page, datasetId);

  await mockFields(page, datasetId);

  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/records?include=responses&include=suggestions&offset=0&limit=10&response_status=pending&response_status=draft`,
    async (route) => {
      await route.fulfill({
        json: {
          items: [recordOne],
        },
      });
    }
  );

  return recordOne;
};

export const mockRecordResponses = async (
  page: Page,
  recordId: string,
  status: "submitted" | "discarded"
) => {
  await page.route(
    `*/**/api/v1/records/${recordId}/responses`,
    async (route, request) => {
      await route.fulfill({
        json: {
          id: recordId,
          values: request.postDataJSON().values,
          status,
          user_id: "3e760b76-e19a-480a-b436-a85812b98843",
          inserted_at: "2023-07-28T14:45:37",
          updated_at: "2023-07-28T14:45:37",
        },
      });
    }
  );
};

const debounce = useDebounce(1000);
export const mockDraftRecord = async (page: Page, recordId: string) => {
  await page.route(`*/**/api/v1/responses/${recordId}`, async (route) => {
    await debounce.wait();
    await route.fulfill({
      json: {
        values: {},
        status: "draft",
        user_id: "3e760b76-e19a-480a-b436-a85812b98843",
        inserted_at: "2023-07-28T14:45:37",
        updated_at: "2023-07-28T14:45:37",
      },
    });

    debounce.stop();
  });

  await page.route(
    `*/**/api/v1/records/${recordId}/responses`,
    async (route) => {
      await debounce.wait();
      await route.fulfill({
        json: {
          id: recordId,
          values: {},
          status: "draft",
          user_id: "3e760b76-e19a-480a-b436-a85812b98843",
          inserted_at: "2023-07-28T14:45:37",
          updated_at: "2023-07-28T14:45:37",
        },
      });

      debounce.stop();
    }
  );
};

export const mockRecordWith12Ranking = async (
  page: Page,
  { datasetId, workspaceId }: DatasetData
) => {
  await mockFeedbackTaskDataset(page, { datasetId, workspaceId });

  await mockQuestionWith12Ranking(page, datasetId);

  await mockFields(page, datasetId);

  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/records?include=responses&include=suggestions&offset=0&limit=10&response_status=pending&response_status=draft`,
    async (route) => {
      await route.fulfill({
        json: {
          items: [recordFor12rankingA, recordFor12rankingB],
        },
      });
    }
  );
  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/records?include=responses&include=suggestions&offset=2&limit=10&response_status=pending&response_status=draft`,
    async (route) => {
      await route.fulfill({
        json: {
          items: [],
        },
      });
    }
  );
};

export const mockRecordWithRating = async (
  page: Page,
  { datasetId, workspaceId }: DatasetData
) => {
  await mockFeedbackTaskDataset(page, { datasetId, workspaceId });

  await mockQuestionWithRating(page, datasetId);

  await mockFields(page, datasetId);

  await page.route(
    `*/**/api/v1/me/datasets/${datasetId}/records?include=responses&include=suggestions&offset=0&limit=10&response_status=pending&response_status=draft`,
    async (route) => {
      await route.fulfill({
        json: {
          items: [recordForRating],
        },
      });
    }
  );
};
