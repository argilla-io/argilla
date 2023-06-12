import { shallowMount, RouterLinkStub } from "@vue/test-utils";
import QuestionsFormComponent from "./QuestionsForm.component";
import BaseButton from "@/components/base/BaseButton";
import TextAreaComponent from "./fields/text-area/TextArea.component";
import RatingComponent from "./fields/rating/Rating.component";
import SingleLabelComponent from "./fields/single-label/SingleLabel.component";
import MultiLabelComponent from "./fields/multi-label/MultiLabel.component";

jest.mock(
  "@/models/feedback-task-model/record-response/recordResponse.queries",
  () => ({
    getRecordResponsesIdByRecordId: ({ userId, recordId }) => "response-id",
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

beforeEach(() => {});

describe("QuestionsFormComponent when initialInputs is empty", () => {
  it("render the component", () => {
    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
        TextAreaComponent,
      },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs: [],
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.is(QuestionsFormComponent)).toBe(true);
    expect(wrapper.vm.userId).toBe("user-id");
    expect(wrapper.vm.responseId).toBe("response-id");
    expect(wrapper.vm.initialInputs).toStrictEqual([]);
    expect(wrapper.vm.inputs).toStrictEqual([]);
    expect(wrapper.vm.isSomeRequiredQuestionHaveNoAnswer).toBe(false);
    expect(wrapper.vm.renderForm).toBe(1);
    expect(wrapper.vm.isError).toBe(false);

    // NOTE - if the form have been touched, the form will have the class '--edited-form'
    expect(wrapper.vm.isFormUntouched).toBe(true);
    expect(wrapper.classes()).not.toContain("--edited-form");

    const titleWrapper = wrapper.find(".questions-form__title");
    expect(titleWrapper.text()).toBe("Submit your feedback");

    const formGroupWrapper = wrapper.find(".form-group");
    expect(formGroupWrapper.exists()).toBeFalsy();
  });
  it("have a redirection nuxt-link to open in a new tab the dataset settings", () => {
    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs: [],
      },
    };

    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.findComponent(RouterLinkStub).props().to).toStrictEqual({
      name: "dataset-id-settings",
      params: { id: "datasetId" },
    });
  });
  it("render ONE TextArea component if there is ONE input item with a componentType === FREE_TEXT", () => {
    const initialInputs = [
      {
        $id: "01c8d729-2408-4161-8015-66133d70df49",
        id: "01c8d729-2408-4161-8015-66133d70df49",
        name: "prompt-edit",
        dataset_id: "2c66550c-99be-402c-9176-0a7d57834bb8",
        order: 0,
        question: "How would you edit the prompt to make it clearer?",
        options: [{ id: "prompt-edit", value: "", text: "" }],
        placeholder: null,
        is_required: false,
        component_type: "FREE_TEXT",
        description:
          "This question is optional. If you think the prompt is clear enough, leave it empty.",
        settings: { type: "text", use_markdown: true },
        response_id: null,
      },
    ];

    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      components: { TextAreaComponent },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs,
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.vm.inputs).toStrictEqual(initialInputs);
    const formGroupWrapper = wrapper.find(".form-group");

    const TextAreaWrapper = wrapper.findComponent({
      name: "TextAreaComponent",
    });
    expect(formGroupWrapper.exists()).toBeTruthy();
    expect(TextAreaWrapper.exists()).toBeTruthy();

    const childNodes = wrapper.findAllComponents({ name: "TextAreaComponent" });
    expect(childNodes.length).toBe(1);
  });
  it("render TWO TextArea component if there is TWO inputs item with a componentType === FREE_TEXT", () => {
    const initialInputs = [
      {
        $id: "5591f1f4-71d5-4c17-ae8e-7831134f889e",
        id: "5591f1f4-71d5-4c17-ae8e-7831134f889e",
        name: "correction_reply_2",
        dataset_id: "ee9c03da-1c40-43d8-8e0a-acd02433bfb2",
        order: 8,
        question: "Propose a correction for reply no.2",
        options: [
          { id: "correction_reply_2", value: "adfsgaedfv", is_selected: false },
        ],
        placeholder: null,
        is_required: false,
        component_type: "FREE_TEXT",
        description:
          "If needed, provide a corrected or alternative text for reply_2.",
        settings: { type: "text", use_markdown: false },
        response_id: "e9115637-6047-436d-b5c6-750efe20f4e4",
      },
      {
        $id: "2e176bc1-2601-444d-9e58-c3a97e5a9cdc",
        id: "2e176bc1-2601-444d-9e58-c3a97e5a9cdc",
        name: "comments",
        dataset_id: "ee9c03da-1c40-43d8-8e0a-acd02433bfb2",
        order: 9,
        question: "Comments",
        options: [{ id: "comments", value: "", is_selected: false }],
        placeholder: null,
        is_required: false,
        component_type: "FREE_TEXT",
        description: null,
        settings: { type: "text", use_markdown: false },
        response_id: "e9115637-6047-436d-b5c6-750efe20f4e4",
      },
    ];

    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      components: { TextAreaComponent },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs,
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.vm.inputs).toStrictEqual(initialInputs);
    const formGroupWrapper = wrapper.find(".form-group");

    const TextAreaWrapper = wrapper.findComponent({
      name: "TextAreaComponent",
    });
    expect(formGroupWrapper.exists()).toBeTruthy();
    expect(TextAreaWrapper.exists()).toBeTruthy();

    const childNodes = wrapper.findAllComponents({ name: "TextAreaComponent" });
    expect(childNodes.length).toBe(2);
  });
  it("render ONE Rating component if there is ONE input item with a componentType === RATING", () => {
    const initialInputs = [
      {
        $id: "456fde6e-68d1-484d-97bc-6e3fbfde88af",
        id: "456fde6e-68d1-484d-97bc-6e3fbfde88af",
        name: "preferred_reply",
        dataset_id: "ee9c03da-1c40-43d8-8e0a-acd02433bfb2",
        order: 0,
        question: "Select your preferred reply",
        options: [
          { id: "preferred_reply_1", text: 1, value: 1, is_selected: true },
          { id: "preferred_reply_2", text: 2, value: 2, is_selected: false },
        ],
        placeholder: null,
        is_required: true,
        component_type: "RATING",
        description: null,
        settings: { type: "rating", options: [{ value: 1 }, { value: 2 }] },
        response_id: "e9115637-6047-436d-b5c6-750efe20f4e4",
      },
    ];

    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      components: { RatingComponent },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs,
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.vm.inputs).toStrictEqual(initialInputs);
    const formGroupWrapper = wrapper.find(".form-group");

    const RatingWrapper = wrapper.findComponent({
      name: "RatingComponent",
    });
    expect(formGroupWrapper.exists()).toBeTruthy();
    expect(RatingWrapper.exists()).toBeTruthy();

    const childNodes = wrapper.findAllComponents({ name: "RatingComponent" });
    expect(childNodes.length).toBe(1);
  });
  it("render TWO Rating component if there is TWO inputs item with a componentType === RATING", () => {
    const initialInputs = [
      {
        $id: "456fde6e-68d1-484d-97bc-6e3fbfde88af",
        id: "456fde6e-68d1-484d-97bc-6e3fbfde88af",
        name: "preferred_reply",
        dataset_id: "ee9c03da-1c40-43d8-8e0a-acd02433bfb2",
        order: 0,
        question: "Select your preferred reply",
        options: [
          { id: "preferred_reply_1", text: 1, value: 1, is_selected: true },
          { id: "preferred_reply_2", text: 2, value: 2, is_selected: false },
        ],
        placeholder: null,
        is_required: true,
        component_type: "RATING",
        description: null,
        settings: { type: "rating", options: [{ value: 1 }, { value: 2 }] },
        response_id: "e9115637-6047-436d-b5c6-750efe20f4e4",
      },
      {
        $id: "5d8d0e16-dd77-4bd9-a0e9-f64f37417d74",
        id: "5d8d0e16-dd77-4bd9-a0e9-f64f37417d74",
        name: "quality_reply_1",
        dataset_id: "ee9c03da-1c40-43d8-8e0a-acd02433bfb2",
        order: 1,
        question: "Rate the overall quality of reply no.1",
        options: [
          { id: "quality_reply_1_1", text: 1, value: 1, is_selected: false },
          { id: "quality_reply_1_2", text: 2, value: 2, is_selected: true },
          { id: "quality_reply_1_3", text: 3, value: 3, is_selected: false },
          { id: "quality_reply_1_4", text: 4, value: 4, is_selected: false },
          { id: "quality_reply_1_5", text: 5, value: 5, is_selected: false },
        ],
        placeholder: null,
        is_required: true,
        component_type: "RATING",
        description:
          "Check if reply_1 has typos or errors and select your score, 1 being very bad and 5 being very good.",
        settings: {
          type: "rating",
          options: [
            { value: 1 },
            { value: 2 },
            { value: 3 },
            { value: 4 },
            { value: 5 },
          ],
        },
        response_id: "e9115637-6047-436d-b5c6-750efe20f4e4",
      },
    ];

    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      components: { RatingComponent },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs,
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.vm.inputs).toStrictEqual(initialInputs);
    const formGroupWrapper = wrapper.find(".form-group");

    const RatingWrapper = wrapper.findComponent({
      name: "RatingComponent",
    });
    expect(formGroupWrapper.exists()).toBeTruthy();
    expect(RatingWrapper.exists()).toBeTruthy();

    const childNodes = wrapper.findAllComponents({ name: "RatingComponent" });
    expect(childNodes.length).toBe(2);
  });
  it("render ONE SingleLabel component if there is ONE input item with a componentType === SINGLE_LABEL", () => {
    const initialInputs = [
      {
        $id: "16f85e36-e144-49c8-af96-68a86189695d",
        id: "16f85e36-e144-49c8-af96-68a86189695d",
        name: "question-1",
        dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
        order: 0,
        question: "Question-1",
        options: [
          {
            id: "question-1_label-1",
            value: "label-1",
            text: "label-1",
            is_selected: false,
          },
          {
            id: "question-1_label-2",
            value: "label-2",
            text: "label-2",
            is_selected: false,
          },
          {
            id: "question-1_label-3",
            value: "label-3",
            text: "label-3",
            is_selected: false,
          },
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
        response_id: null,
      },
    ];

    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      components: { SingleLabelComponent },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs,
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.vm.inputs).toStrictEqual(initialInputs);
    const formGroupWrapper = wrapper.find(".form-group");

    const SingleLabelWrapper = wrapper.findComponent({
      name: "SingleLabelComponent",
    });
    expect(formGroupWrapper.exists()).toBeTruthy();
    expect(SingleLabelWrapper.exists()).toBeTruthy();

    const childNodes = wrapper.findAllComponents({
      name: "SingleLabelComponent",
    });
    expect(childNodes.length).toBe(1);
  });
  it("render TWO SingleLabel component if there is TWO inputs item with a componentType === SINGLE_LABEL", () => {
    const initialInputs = [
      {
        $id: "16f85e36-e144-49c8-af96-68a86189695d",
        id: "16f85e36-e144-49c8-af96-68a86189695d",
        name: "question-1",
        dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
        order: 0,
        question: "Question-1",
        options: [
          {
            id: "question-1_label-1",
            value: "label-1",
            text: "label-1",
            is_selected: false,
          },
          {
            id: "question-1_label-2",
            value: "label-2",
            text: "label-2",
            is_selected: false,
          },
          {
            id: "question-1_label-3",
            value: "label-3",
            text: "label-3",
            is_selected: false,
          },
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
        response_id: null,
      },
      {
        $id: "c1dc9010-7d64-4357-8cae-03c3a14140b2",
        id: "c1dc9010-7d64-4357-8cae-03c3a14140b2",
        name: "question-2",
        dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
        order: 1,
        question: "Question-2",
        options: [
          {
            id: "question-2_label-4",
            value: "label-4",
            text: "label-4",
            is_selected: false,
          },
          {
            id: "question-2_label-5",
            value: "label-5",
            text: "label-5",
            is_selected: false,
          },
          {
            id: "question-2_label-6",
            value: "label-6",
            text: "label-6",
            is_selected: false,
          },
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
        response_id: null,
      },
    ];

    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      components: { SingleLabelComponent },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs,
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.vm.inputs).toStrictEqual(initialInputs);
    const formGroupWrapper = wrapper.find(".form-group");

    const SingleLabelWrapper = wrapper.findComponent({
      name: "SingleLabelComponent",
    });
    expect(formGroupWrapper.exists()).toBeTruthy();
    expect(SingleLabelWrapper.exists()).toBeTruthy();

    const childNodes = wrapper.findAllComponents({
      name: "SingleLabelComponent",
    });
    expect(childNodes.length).toBe(2);
  });
  it("render ONE MultiLabel component if there is ONE input item with a componentType === MULTI_LABEL", () => {
    const initialInputs = [
      {
        $id: "70392e94-f139-43c7-9cab-7a748a9446c2",
        id: "70392e94-f139-43c7-9cab-7a748a9446c2",
        name: "question-1",
        dataset_id: "349ab6e0-450f-4b81-a154-c07bfb12ff5f",
        order: 0,
        question: "Question-1",
        options: [
          {
            id: "question-1_label-1",
            text: "label-1",
            value: "label-1",
            is_selected: true,
          },
          {
            id: "question-1_label-2",
            text: "label-2",
            value: "label-2",
            is_selected: true,
          },
          {
            id: "question-1_label-3",
            text: "label-3",
            value: "label-3",
            is_selected: true,
          },
        ],
        placeholder: null,
        is_required: true,
        component_type: "MULTI_LABEL",
        description: null,
        settings: {
          type: "multi_label_selection",
          options: [
            { value: "label-1", text: "label-1", description: null },
            { value: "label-2", text: "label-2", description: null },
            { value: "label-3", text: "label-3", description: null },
          ],
          visible_options: null,
        },
        response_id: "0172b478-4a5b-42f7-a3cd-42743d905ef9",
      },
    ];

    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      components: { MultiLabelComponent },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs,
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.vm.inputs).toStrictEqual(initialInputs);
    const formGroupWrapper = wrapper.find(".form-group");

    const MultiLabelWrapper = wrapper.findComponent({
      name: "MultiLabelComponent",
    });
    expect(formGroupWrapper.exists()).toBeTruthy();
    expect(MultiLabelWrapper.exists()).toBeTruthy();

    const childNodes = wrapper.findAllComponents({
      name: "MultiLabelComponent",
    });
    expect(childNodes.length).toBe(1);
  });
  it("render TWO MultiLabel component if there is TWO inputs item with a componentType === MULTI_LABEL", () => {
    const initialInputs = [
      {
        $id: "70392e94-f139-43c7-9cab-7a748a9446c2",
        id: "70392e94-f139-43c7-9cab-7a748a9446c2",
        name: "question-1",
        dataset_id: "349ab6e0-450f-4b81-a154-c07bfb12ff5f",
        order: 0,
        question: "Question-1",
        options: [
          {
            id: "question-1_label-1",
            text: "label-1",
            value: "label-1",
            is_selected: true,
          },
          {
            id: "question-1_label-2",
            text: "label-2",
            value: "label-2",
            is_selected: true,
          },
          {
            id: "question-1_label-3",
            text: "label-3",
            value: "label-3",
            is_selected: true,
          },
        ],
        placeholder: null,
        is_required: true,
        component_type: "MULTI_LABEL",
        description: null,
        settings: {
          type: "multi_label_selection",
          options: [
            { value: "label-1", text: "label-1", description: null },
            { value: "label-2", text: "label-2", description: null },
            { value: "label-3", text: "label-3", description: null },
          ],
          visible_options: null,
        },
        response_id: "0172b478-4a5b-42f7-a3cd-42743d905ef9",
      },
      {
        $id: "f12e5900-65c1-4606-8686-22a5e07b63ca",
        id: "f12e5900-65c1-4606-8686-22a5e07b63ca",
        name: "question-2",
        dataset_id: "349ab6e0-450f-4b81-a154-c07bfb12ff5f",
        order: 1,
        question: "Question-2",
        options: [
          {
            id: "question-2_label-4",
            text: "label-4",
            value: "label-4",
            is_selected: true,
          },
          {
            id: "question-2_label-5",
            text: "label-5",
            value: "label-5",
            is_selected: true,
          },
          {
            id: "question-2_label-6",
            text: "label-6",
            value: "label-6",
            is_selected: false,
          },
        ],
        placeholder: null,
        is_required: true,
        component_type: "MULTI_LABEL",
        description: null,
        settings: {
          type: "multi_label_selection",
          options: [
            { value: "label-4", text: "label-4", description: null },
            { value: "label-5", text: "label-5", description: null },
            { value: "label-6", text: "label-6", description: null },
          ],
          visible_options: null,
        },
        response_id: "0172b478-4a5b-42f7-a3cd-42743d905ef9",
      },
    ];

    const options = {
      mocks: {
        $auth: authMock,
      },
      stubs: {
        NuxtLink: RouterLinkStub,
        BaseButton,
      },
      components: { MultiLabelComponent },
      propsData: {
        datasetId: "datasetId",
        recordId: "recordId",
        recordStatus: "pending",
        initialInputs,
      },
    };
    const wrapper = shallowMount(QuestionsFormComponent, options);

    expect(wrapper.vm.inputs).toStrictEqual(initialInputs);
    const formGroupWrapper = wrapper.find(".form-group");

    const MultiLabelWrapper = wrapper.findComponent({
      name: "MultiLabelComponent",
    });
    expect(formGroupWrapper.exists()).toBeTruthy();
    expect(MultiLabelWrapper.exists()).toBeTruthy();

    const childNodes = wrapper.findAllComponents({
      name: "MultiLabelComponent",
    });
    expect(childNodes.length).toBe(2);
  });
});
