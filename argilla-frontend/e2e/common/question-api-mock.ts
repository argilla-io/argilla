import { Page } from "@playwright/test";

const questions = [
  {
    id: "045c18d5-57b6-408a-8db3-bc11b9f54541",
    name: "sentiment",
    title: "Sentiment",
    description: "Sentiment of the text",
    required: true,
    settings: {
      type: "label_selection",
      options: [
        {
          value: "positive",
          text: "Positive",
          description: "Texts with a positive intent",
        },
        {
          value: "very_positive",
          text: "Very Positive",
          description: "Texts with a very strong positive intent",
        },
        {
          value: "negative",
          text: "Negative",
          description: "Texts with a negative intent",
        },
        {
          value: "neutral",
          text: "Neutral",
          description: "Texts with a neutral intent",
        },
        {
          value: "happy",
          text: "Happy",
          description: "Texts expressing happiness",
        },
        {
          value: "sad",
          text: "Sad",
          description: "Texts expressing sadness",
        },
        {
          value: "angry",
          text: "Angry",
          description: "Texts expressing anger",
        },
        {
          value: "excited",
          text: "Excited",
          description: "Texts expressing excitement",
        },
        {
          value: "disappointed",
          text: "Disappointed",
          description: "Texts expressing disappointment",
        },
        {
          value: "surprised",
          text: "Surprised",
          description: "Texts expressing surprise",
        },
        {
          value: "grateful",
          text: "Grateful",
          description: "Texts expressing gratitude",
        },
        {
          value: "loving",
          text: "Loving",
          description: "Texts expressing love and affection",
        },
        {
          value: "optimistic",
          text: "Optimistic",
          description: "Texts expressing optimism",
        },
        {
          value: "proud",
          text: "Proud",
          description: "Texts expressing pride",
        },
        {
          value: "worried",
          text: "Worried",
          description: "Texts expressing worry or concern",
        },
        {
          value: "hopeful",
          text: "Hopeful",
          description: "Texts expressing hope",
        },
        {
          value: "bored",
          text: "Bored",
          description: "Texts expressing boredom",
        },
        {
          value: "amused",
          text: "Amused",
          description: "Texts expressing amusement",
        },
        {
          value: "confused",
          text: "Confused",
          description: "Texts expressing confusion",
        },
        {
          value: "frustrated",
          text: "Frustrated",
          description: "Texts expressing frustration",
        },
        {
          value: "content",
          text: "Content",
          description: "Texts expressing contentment",
        },
        {
          value: "over_the_moon",
          text: "Over the Moon",
          description: "Texts expressing extreme happiness",
        },
        {
          value: "heartbroken",
          text: "Heartbroken",
          description: "Texts expressing extreme sadness",
        },
        {
          value: "furious",
          text: "Furious",
          description: "Texts expressing extreme anger",
        },
        {
          value: "ecstatic",
          text: "Ecstatic",
          description: "Texts expressing overwhelming joy",
        },
        {
          value: "devastated",
          text: "Devastated",
          description: "Texts expressing extreme grief",
        },
        {
          value: "anxious",
          text: "Anxious",
          description: "Texts expressing extreme worry",
        },
        {
          value: "terrified",
          text: "Terrified",
          description: "Texts expressing extreme fear",
        },
        {
          value: "delighted",
          text: "Delighted",
          description: "Texts expressing extreme happiness",
        },
        {
          value: "disgusted",
          text: "Disgusted",
          description: "Texts expressing extreme disgust",
        },
        {
          value: "jealous",
          text: "Jealous",
          description: "Texts expressing extreme envy",
        },
        {
          value: "lonely",
          text: "Lonely",
          description: "Texts expressing extreme loneliness",
        },
        {
          value: "shocked",
          text: "Shocked",
          description: "Texts expressing extreme surprise",
        },
        {
          value: "satisfied",
          text: "Satisfied",
          description: "Texts expressing satisfaction",
        },
        {
          value: "relaxed",
          text: "Relaxed",
          description: "Texts expressing relaxation",
        },
        {
          value: "thankful",
          text: "Thankful",
          description: "Texts expressing gratitude",
        },
        {
          value: "annoyed",
          text: "Annoyed",
          description: "Texts expressing annoyance",
        },
        {
          value: "guilty",
          text: "Guilty",
          description: "Texts expressing guilt",
        },
        {
          value: "embarrassed",
          text: "Embarrassed",
          description: "Texts expressing embarrassment",
        },
        {
          value: "ashamed",
          text: "Ashamed",
          description: "Texts expressing shame",
        },
        {
          value: "pessimistic",
          text: "Pessimistic",
          description: "Texts expressing pessimism",
        },
        {
          value: "nostalgic",
          text: "Nostalgic",
          description: "Texts expressing nostalgia",
        },
        {
          value: "sympathetic",
          text: "Sympathetic",
          description: "Texts expressing sympathy",
        },
        {
          value: "fearful",
          text: "Fearful",
          description: "Texts expressing fear",
        },
        {
          value: "hurt",
          text: "Hurt",
          description: "Texts expressing hurt",
        },
      ],
      visible_options: 10,
    },
    inserted_at: "2023-07-18T07:43:35",
    updated_at: "2023-07-18T07:43:35",
  },
  {
    id: "682dd011-6a8a-452e-8900-483279c6acee",
    name: "sentiment-multi-label",
    title: "Sentiment Multi Label",
    description: "Sentiment of the text",
    required: true,
    settings: {
      type: "multi_label_selection",
      options: [
        {
          value: "positive",
          text: "Positive",
          description: "Texts with a positive intent",
        },
        {
          value: "very_positive",
          text: "Very Positive",
          description: "Texts with a very strong positive intent",
        },
        {
          value: "negative",
          text: "Negative",
          description: "Texts with a negative intent",
        },
        {
          value: "neutral",
          text: "Neutral",
          description: "Texts with a neutral intent",
        },
        {
          value: "happy",
          text: "Happy",
          description: "Texts expressing happiness",
        },
        {
          value: "sad",
          text: "Sad",
          description: "Texts expressing sadness",
        },
        {
          value: "angry",
          text: "Angry",
          description: "Texts expressing anger",
        },
        {
          value: "excited",
          text: "Excited",
          description: "Texts expressing excitement",
        },
        {
          value: "disappointed",
          text: "Disappointed",
          description: "Texts expressing disappointment",
        },
        {
          value: "surprised",
          text: "Surprised",
          description: "Texts expressing surprise",
        },
        {
          value: "grateful",
          text: "Grateful",
          description: "Texts expressing gratitude",
        },
        {
          value: "loving",
          text: "Loving",
          description: "Texts expressing love and affection",
        },
        {
          value: "optimistic",
          text: "Optimistic",
          description: "Texts expressing optimism",
        },
        {
          value: "proud",
          text: "Proud",
          description: "Texts expressing pride",
        },
        {
          value: "worried",
          text: "Worried",
          description: "Texts expressing worry or concern",
        },
        {
          value: "hopeful",
          text: "Hopeful",
          description: "Texts expressing hope",
        },
        {
          value: "bored",
          text: "Bored",
          description: "Texts expressing boredom",
        },
        {
          value: "amused",
          text: "Amused",
          description: "Texts expressing amusement",
        },
        {
          value: "confused",
          text: "Confused",
          description: "Texts expressing confusion",
        },
        {
          value: "frustrated",
          text: "Frustrated",
          description: "Texts expressing frustration",
        },
        {
          value: "content",
          text: "Content",
          description: "Texts expressing contentment",
        },
        {
          value: "over_the_moon",
          text: "Over the Moon",
          description: "Texts expressing extreme happiness",
        },
        {
          value: "heartbroken",
          text: "Heartbroken",
          description: "Texts expressing extreme sadness",
        },
        {
          value: "furious",
          text: "Furious",
          description: "Texts expressing extreme anger",
        },
        {
          value: "ecstatic",
          text: "Ecstatic",
          description: "Texts expressing overwhelming joy",
        },
        {
          value: "devastated",
          text: "Devastated",
          description: "Texts expressing extreme grief",
        },
        {
          value: "anxious",
          text: "Anxious",
          description: "Texts expressing extreme worry",
        },
        {
          value: "terrified",
          text: "Terrified",
          description: "Texts expressing extreme fear",
        },
        {
          value: "delighted",
          text: "Delighted",
          description: "Texts expressing extreme happiness",
        },
        {
          value: "disgusted",
          text: "Disgusted",
          description: "Texts expressing extreme disgust",
        },
        {
          value: "jealous",
          text: "Jealous",
          description: "Texts expressing extreme envy",
        },
        {
          value: "lonely",
          text: "Lonely",
          description: "Texts expressing extreme loneliness",
        },
        {
          value: "shocked",
          text: "Shocked",
          description: "Texts expressing extreme surprise",
        },
        {
          value: "satisfied",
          text: "Satisfied",
          description: "Texts expressing satisfaction",
        },
        {
          value: "relaxed",
          text: "Relaxed",
          description: "Texts expressing relaxation",
        },
        {
          value: "thankful",
          text: "Thankful",
          description: "Texts expressing gratitude",
        },
        {
          value: "annoyed",
          text: "Annoyed",
          description: "Texts expressing annoyance",
        },
        {
          value: "guilty",
          text: "Guilty",
          description: "Texts expressing guilt",
        },
        {
          value: "embarrassed",
          text: "Embarrassed",
          description: "Texts expressing embarrassment",
        },
        {
          value: "ashamed",
          text: "Ashamed",
          description: "Texts expressing shame",
        },
        {
          value: "pessimistic",
          text: "Pessimistic",
          description: "Texts expressing pessimism",
        },
        {
          value: "nostalgic",
          text: "Nostalgic",
          description: "Texts expressing nostalgia",
        },
        {
          value: "sympathetic",
          text: "Sympathetic",
          description: "Texts expressing sympathy",
        },
        {
          value: "fearful",
          text: "Fearful",
          description: "Texts expressing fear",
        },
        {
          value: "hurt",
          text: "Hurt",
          description: "Texts expressing hurt",
        },
      ],
      visible_options: 10,
    },
    inserted_at: "2023-07-18T07:43:35",
    updated_at: "2023-07-18T07:43:35",
  },
  {
    id: "58f80371-7302-4151-abbb-ab180d229f95",
    name: "review-rating",
    title: "Review Rating",
    description: "Rating of the review",
    required: false,
    settings: {
      type: "rating",
      options: [
        {
          value: 1,
        },
        {
          value: 2,
        },
        {
          value: 3,
        },
        {
          value: 4,
        },
        {
          value: 5,
        },
      ],
    },
    inserted_at: "2023-07-18T07:43:35",
    updated_at: "2023-07-18T07:43:35",
  },
  {
    id: "7a642861-5c68-418e-8e9f-3fb95d837b86",
    name: "review-review",
    title: "Review of the Review (Review Inception)",
    description: "What do you think about this review?",
    required: false,
    settings: {
      type: "text",
      use_markdown: false,
    },
    inserted_at: "2023-07-18T07:43:36",
    updated_at: "2023-07-18T07:43:36",
  },
  {
    id: "b42c4d1a-6a87-42c7-bfcb-5e1df333c361",
    name: "ranking",
    title: "Ranking",
    description: "Random ranking question",
    required: false,
    settings: {
      type: "ranking",
      options: [
        {
          value: "option-a",
          text: "Option A",
          description: "Option A",
        },
        {
          value: "option-b",
          text: "Option B",
          description: "Option B",
        },
        {
          value: "option-c",
          text: "Option C",
          description: "Option C",
        },
        {
          value: "option-d",
          text: "Option D",
          description: "Option D",
        },
      ],
    },
    inserted_at: "2023-07-18T07:43:36",
    updated_at: "2023-07-18T07:43:36",
  },
];

const rankingQuestionWith12Slots = [
  {
    id: "9f23fcdb-a57a-4568-a9d8-2360315e9fd3",
    name: "rating",
    title: "Rating",
    description: null,
    required: true,
    settings: {
      type: "ranking",
      options: [
        {
          value: "1",
          text: "1",
          description: null,
        },
        {
          value: "2",
          text: "2",
          description: null,
        },
        {
          value: "3",
          text: "3",
          description: null,
        },
        {
          value: "4",
          text: "4",
          description: null,
        },
        {
          value: "5",
          text: "5",
          description: null,
        },
        {
          value: "6",
          text: "6",
          description: null,
        },
        {
          value: "7",
          text: "7",
          description: null,
        },
        {
          value: "8",
          text: "8",
          description: null,
        },
        {
          value: "9",
          text: "9",
          description: null,
        },
        {
          value: "10",
          text: "10",
          description: null,
        },
        {
          value: "11",
          text: "11",
          description: null,
        },
        {
          value: "12",
          text: "12",
          description: null,
        },
      ],
    },
    inserted_at: "2023-07-26T12:15:01",
    updated_at: "2023-07-26T12:15:01",
  },
];

const ratingQuestions = [
  {
    id: "7b711f4b-c901-4e65-bbac-a80a341baf84",
    name: "rating",
    title: "Rating",
    description: null,
    required: true,
    settings: {
      type: "rating",
      options: [
        {
          value: 1,
        },
        {
          value: 2,
        },
        {
          value: 3,
        },
        {
          value: 4,
        },
        {
          value: 5,
        },
        {
          value: 6,
        },
        {
          value: 7,
        },
        {
          value: 8,
        },
        {
          value: 9,
        },
        {
          value: 10,
        },
      ],
    },
    inserted_at: "2023-07-21T09:23:19",
    updated_at: "2023-07-21T09:23:19",
  },
];

const longAndShortQuestions = [
  {
    id: "045c18d5-57b6-408a-8db3-bc11b9f54541",
    name: "sentiment",
    title: "Sentiment",
    description: "Sentiment of the text",
    required: true,
    settings: {
      type: "label_selection",
      options: [
        {
          value: "a",
          text: "A",
          description: "Texts with a A intent",
        },
        {
          value: "loong-single-label-questions-with-more-than-20",
          text: "Single Loong single label question with more than 20 letter",
          description: "Texts with a long intent",
        },
      ],
      visible_options: 10,
    },
    inserted_at: "2023-07-18T07:43:35",
    updated_at: "2023-07-18T07:43:35",
  },
  {
    id: "682dd011-6a8a-452e-8900-483279c6acee",
    name: "sentiment-multi-label",
    title: "Sentiment Multi Label",
    description: "Sentiment of the text",
    required: true,
    settings: {
      type: "multi_label_selection",
      options: [
        {
          value: "a",
          text: "A",
          description: "Texts with a A intent",
        },
        {
          value: "loong-single-label-questions-with-more-than-20",
          text: "Multi Loong single label question with more than 20 letter",
          description: "Texts with a long intent",
        },
      ],
      visible_options: 10,
    },
    inserted_at: "2023-07-18T07:43:35",
    updated_at: "2023-07-18T07:43:35",
  },
];

export const mockQuestion = async (page: Page, datasetId: string) => {
  await page.route(
    `*/**/api/v1/datasets/${datasetId}/questions`,
    async (route) => {
      await route.fulfill({
        json: {
          items: questions,
        },
      });
    }
  );
};

export const mockQuestionWith12Ranking = async (
  page: Page,
  datasetId: string
) => {
  await page.route(
    `*/**/api/v1/datasets/${datasetId}/questions`,
    async (route) => {
      await route.fulfill({
        json: {
          items: rankingQuestionWith12Slots,
        },
      });
    }
  );
};

export const mockQuestionWithRating = async (page: Page, datasetId: string) => {
  await page.route(
    `*/**/api/v1/datasets/${datasetId}/questions`,
    async (route) => {
      await route.fulfill({
        json: {
          items: ratingQuestions,
        },
      });
    }
  );
};

export const mockQuestionLongAndShortQuestions = async (
  page: Page,
  datasetId: string
) => {
  await page.route(
    `*/**/api/v1/datasets/${datasetId}/questions`,
    async (route) => {
      await route.fulfill({
        json: {
          items: longAndShortQuestions,
        },
      });
    }
  );
};
