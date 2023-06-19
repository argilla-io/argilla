import { shallowMount } from "@vue/test-utils";
import CenterFeedbackTaskComponent from "./CenterFeedbackTask.content";

describe("CenterFeedbackTaskComponent", () => {
  it("render the BaseLoading component while fetching data", () => {
    const options = {
      stubs: ["RecordFeedbackTaskAndQuestionnaireContent", "BaseLoading"],
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

    const BaseLoadingWrapper = wrapper.findComponent({ name: "BaseLoading" });
    expect(BaseLoadingWrapper.exists()).toBe(true);

    const RecordFeedbackTaskAndQuestionnaireContentWrapper =
      wrapper.findComponent({
        name: "RecordFeedbackTaskAndQuestionnaireContent",
      });
    expect(RecordFeedbackTaskAndQuestionnaireContentWrapper.exists()).toBe(
      false
    );
  });
  it("render the RecordFeedbackTaskAndQuestionnaireContent component after fetching data", () => {
    const options = {
      stubs: ["RecordFeedbackTaskAndQuestionnaireContent", "BaseLoading"],
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

    const BaseLoadingWrapper = wrapper.findComponent({ name: "BaseLoading" });
    expect(BaseLoadingWrapper.exists()).toBe(false);

    const RecordFeedbackTaskAndQuestionnaireContentWrapper =
      wrapper.findComponent({
        name: "RecordFeedbackTaskAndQuestionnaireContent",
      });
    expect(RecordFeedbackTaskAndQuestionnaireContentWrapper.exists()).toBe(
      true
    );
  });
  it.skip("fetch, format and insert data into ORM", () => {
    // TODO -
  });
});
