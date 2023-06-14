import { shallowMount } from "@vue/test-utils";
import RecordFeedbackTaskAndQuestionnaireComponent from "./RecordFeedbackTaskAndQuestionnaire.content";

jest.mock("@/models/feedback-task-model/record/record.queries", () => ({
  isAnyRecordByDatasetId: () => true,
  getRecordWithFieldsAndResponsesByUserId: () => {
    return {
      $id: "dbebb7a9-58b1-455e-ad6c-a927d29cdcbe",
      id: "dbebb7a9-58b1-455e-ad6c-a927d29cdcbe",
      dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
      record_status: "PENDING",
      record_index: 0,
      record_responses: [],
      record_fields: [
        {
          $id: "dbebb7a9-58b1-455e-ad6c-a927d29cdcbe_0",
          id: "dbebb7a9-58b1-455e-ad6c-a927d29cdcbe_0",
          field_name: "prompt",
          text: "PROMPT",
          record_id: "dbebb7a9-58b1-455e-ad6c-a927d29cdcbe",
        },
        {
          $id: "dbebb7a9-58b1-455e-ad6c-a927d29cdcbe_1",
          id: "dbebb7a9-58b1-455e-ad6c-a927d29cdcbe_1",
          field_name: "completion",
          text: "COMPLETION",
          record_id: "dbebb7a9-58b1-455e-ad6c-a927d29cdcbe",
        },
      ],
    };
  },
  isRecordWithRecordIndexByDatasetIdExists: () => true,
}));
jest.mock(
  "@/models/feedback-task-model/dataset-field/datasetField.queries",
  () => ({
    getFieldsByDatasetId: () => {
      return [
        {
          $id: "892ca786-d38d-4bd5-b5c6-cec01a561d21",
          id: "892ca786-d38d-4bd5-b5c6-cec01a561d21",
          name: "prompt",
          dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
          order: 0,
          title: "Prompt",
          is_required: true,
          component_type: "TEXT_FIELD",
          settings: { type: "text", use_markdown: false },
        },
        {
          $id: "aeae41b7-334e-4f7f-9de6-4a053d739785",
          id: "aeae41b7-334e-4f7f-9de6-4a053d739785",
          name: "completion",
          dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
          order: 1,
          title: "Completion",
          is_required: true,
          component_type: "TEXT_FIELD",
          settings: { type: "text", use_markdown: false },
        },
      ];
    },
  })
);
jest.mock(
  "@/models/feedback-task-model/dataset-question/datasetQuestion.queries",
  () => ({
    getQuestionsByDatasetId: () => {
      return [
        {
          $id: "16f85e36-e144-49c8-af96-68a86189695d",
          id: "16f85e36-e144-49c8-af96-68a86189695d",
          name: "question-1",
          dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
          order: 0,
          question: "Question-1",
          options: [
            { id: "question-1_label-1", value: "label-1", text: "label-1" },
            { id: "question-1_label-2", value: "label-2", text: "label-2" },
            { id: "question-1_label-3", value: "label-3", text: "label-3" },
          ],
          placeholder: null,
          is_required: true,
          component_type: "SINGLE_LABEL",
          description: null,
          settings: {
            type: "label_selection",
            options: [
              { value: "label-1", text: "label-1", description: null },
              { value: "label-2", text: "label-2", description: null },
              { value: "label-3", text: "label-3", description: null },
            ],
            visible_options: null,
          },
        },
        {
          $id: "c1dc9010-7d64-4357-8cae-03c3a14140b2",
          id: "c1dc9010-7d64-4357-8cae-03c3a14140b2",
          name: "question-2",
          dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
          order: 1,
          question: "Question-2",
          options: [
            { id: "question-2_label-4", value: "label-4", text: "label-4" },
            { id: "question-2_label-5", value: "label-5", text: "label-5" },
            { id: "question-2_label-6", value: "label-6", text: "label-6" },
          ],
          placeholder: null,
          is_required: true,
          component_type: "SINGLE_LABEL",
          description: null,
          settings: {
            type: "label_selection",
            options: [
              { value: "label-4", text: "label-4", description: null },
              { value: "label-5", text: "label-5", description: null },
              { value: "label-6", text: "label-6", description: null },
            ],
            visible_options: null,
          },
        },
      ];
    },
    getComponentTypeOfQuestionByDatasetIdAndQuestionName: (
      datasetId,
      questionName
    ) => {
      let componentType = "";
      switch (questionName) {
        case "question-free-text":
          componentType = "FREE_TEXT";
          break;
        case "question-rating":
          componentType = "RATING";
          break;
        case "question-single-label":
          componentType = "SINGLE_LABEL";
          break;
        case "question-multi-label":
          componentType = "MULTI_LABEL";
          break;
        default:
        // the component is unknown
      }
      return componentType;
    },
    getOptionsOfQuestionByDatasetIdAndQuestionName: (
      datasetId,
      questionName
    ) => {
      let optionsOfQuestion = "";
      switch (questionName) {
        case "prompt-edit":
          optionsOfQuestion = { id: "prompt-edit", value: "", text: "" };
          break;
        case "question-rating":
          optionsOfQuestion = [
            { id: "question-rating_1", value: 1, text: 1 },
            { id: "question-rating_2", value: 2, text: 2 },
            { id: "question-rating_3", value: 3, text: 3 },
            { id: "question-rating_4", value: 4, text: 4 },
            { id: "question-rating_5", value: 5, text: 5 },
          ];
          break;
        case "question-single-label":
          optionsOfQuestion = [
            {
              id: "question-single-label_label-1",
              value: "label-1",
              text: "label-1",
            },
            {
              id: "question-single-label_label-2",
              value: "label-2",
              text: "label-2",
            },
            {
              id: "question-single-label_label-3",
              value: "label-3",
              text: "label-3",
            },
          ];
          break;
        case "question-multi-label":
          optionsOfQuestion = [
            {
              id: "question-multi-label-1_label-1",
              value: "label-1",
              text: "label-1",
            },
            {
              id: "question-multi-label-1_label-2",
              value: "label-2",
              text: "label-2",
            },
            {
              id: "question-multi-label-1_label-3",
              value: "label-3",
              text: "label-3",
            },
          ];
          break;
        default:
        // the component is unknown
      }
      return optionsOfQuestion;
    },
  })
);

const authMock = {
  loggedIn: true,
  user: {
    id: "user-id",
    first_name: "Juan",
    full_name: "Juan Bueno",
    username: "JeanBon",
    role: "admin",
    workspaces: ["workspace-0", "workspace-1", "workspace-2"],
    api_key: "0000000000",
    inserted_at: "2023-04-27T15:44:23.422345",
    updated_at: "2023-04-27T15:44:23.422345",
  },
};

let wrapper = null;
const options = {
  stubs: ["RecordFeedbackTaskComponent", "QuestionsFormComponent"],
  mocks: {
    $auth: authMock,
    $fetchState: {
      pending: false,
      error: null,
      timestamp: 1686579374810,
    },
  },
  propsData: { datasetId: "datasetId" },
};

beforeEach(() => {
  wrapper = shallowMount(RecordFeedbackTaskAndQuestionnaireComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RecordFeedbackTaskAndQuestionnaireComponent", () => {
  it.skip("render the component", () => {
    // FIXME - there is an error due to missing mock from vuexorm
    expect(wrapper.is(RecordFeedbackTaskAndQuestionnaireComponent)).toBe(true);
  });
});
