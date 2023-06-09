import { shallowMount, RouterLinkStub } from "@vue/test-utils";
import QuestionsFormComponent from "./QuestionsForm.component";
import BaseButton from "@/components/base/BaseButton";
import TextAreaComponent from "./fields/text-area/TextArea.component";
import SingleLabelComponent from "./fields/single-label/SingleLabel.component";
import MultiLabelComponent from "./fields/multi-label/MultiLabel.component";
import RatingComponent from "./fields/rating/Rating.component";
// import { RecordResponseModel } from "@/models/feedback-task-model/record-response/RecordResponse.model";

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
  mocks: {
    $auth: authMock,
    getRecordResponsesIdByRecordId: () => {
      return {};
    },
    // RecordResponseModel: {
    //   query: ({ userId, recordId }) => {
    //     return {
    //       id: "response_id",
    //       options: [],
    //       question_name: null,
    //       record_id: recordId,
    //       user_id: userId,
    //     };
    //   },
    // },
  },
  stubs: {
    NuxtLink: RouterLinkStub,
    BaseButton,
    TextAreaComponent,
    SingleLabelComponent,
    MultiLabelComponent,
    RatingComponent,
  },
  propsData: {
    datasetId: "datasetId",
    recordId: "recordId",
    recordStatus: "pending",
    initialInputs: [],
  },
};

beforeEach(() => {
  wrapper = shallowMount(QuestionsFormComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});
describe.skip("QuestionsFormComponent when initialInputs is empty", () => {
  it("render the component", () => {
    expect(wrapper.is(QuestionsFormComponent)).toBe(true);
    expect(wrapper.vm.userId).toBe("user-id");
    expect(wrapper.vm.responseId).toBe(undefined);
    expect(wrapper.vm.isFormUntouched).toBe(true);
    expect(wrapper.vm.isSomeRequiredQuestionHaveNoAnswer).toBe(true);
  });
  it("have a redirection nuxt-link to open in a new tab the dataset settings", () => {
    expect(wrapper.findComponent(RouterLinkStub).props().to).toStrictEqual({
      name: "dataset-id-settings",
      params: { id: "datasetId" },
    });
  });
});
