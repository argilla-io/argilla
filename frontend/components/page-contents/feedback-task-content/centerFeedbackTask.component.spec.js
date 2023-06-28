import { shallowMount } from "@vue/test-utils";
import CenterFeedbackTaskComponent from "./CenterFeedbackTask.content";

const BaseLoadingStub = {
  name: "BaseLoading",
  template: "<div />",
};

const RecordFeedbackTaskAndQuestionnaireContentStub = {
  name: "RecordFeedbackTaskAndQuestionnaireContent",
  template: "<div />",
  props: ["datasetId"],
};

describe("CenterFeedbackTaskComponent", () => {
  it("render the BaseLoading component while fetching data", () => {
    const options = {
      stubs: {
        BaseLoading: BaseLoadingStub,
        RecordFeedbackTaskAndQuestionnaireContent:
          RecordFeedbackTaskAndQuestionnaireContentStub,
      },
      mocks: {
        $fetchState: {
          pending: true,
          error: null,
          timestamp: 1686579374810,
        },
      },
      propsData: { datasetId: "datasetId" },
    };

    const wrapper = shallowMount(CenterFeedbackTaskComponent, options);

    const BaseLoadingWrapper = wrapper.findComponent(BaseLoadingStub);
    expect(BaseLoadingWrapper.exists()).toBe(true);

    const RecordFeedbackTaskAndQuestionnaireContentWrapper =
      wrapper.findComponent(RecordFeedbackTaskAndQuestionnaireContentStub);
    expect(RecordFeedbackTaskAndQuestionnaireContentWrapper.exists()).toBe(
      false
    );
  });
  it("render the RecordFeedbackTaskAndQuestionnaireContent component after fetching data", () => {
    const options = {
      stubs: {
        BaseLoading: BaseLoadingStub,
        RecordFeedbackTaskAndQuestionnaireContent:
          RecordFeedbackTaskAndQuestionnaireContentStub,
      },
      mocks: {
        $fetchState: {
          pending: false,
          error: null,
          timestamp: 1686579374810,
        },
      },
      propsData: { datasetId: "datasetId" },
    };

    const wrapper = shallowMount(CenterFeedbackTaskComponent, options);

    const BaseLoadingWrapper = wrapper.findComponent(BaseLoadingStub);
    expect(BaseLoadingWrapper.exists()).toBe(false);

    const RecordFeedbackTaskAndQuestionnaireContentWrapper =
      wrapper.findComponent(RecordFeedbackTaskAndQuestionnaireContentStub);
    expect(RecordFeedbackTaskAndQuestionnaireContentWrapper.exists()).toBe(
      true
    );
  });
  it.skip("fetch, format and insert data into ORM", () => {
    // TODO -
  });
});
