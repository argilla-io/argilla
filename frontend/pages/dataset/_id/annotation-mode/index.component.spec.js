import { shallowMount } from "@vue/test-utils";
import AnnotationModePage from "./index";
import HeaderAndTopAndOneColumn from "@/layouts/HeaderAndTopAndOneColumn";
import { setActivePinia, createPinia } from "pinia";
import { GetDatasetByIdUseCase } from "@/v1/domain/usecases/get-dataset-by-id-use-case";
import { useResolveMock } from "~/v1/di/__mocks__/useResolveMock";
import * as useAnnotationModeViewModel from "./useAnnotationModeViewModel";

const pinia = createPinia();
setActivePinia(pinia);

useResolveMock(GetDatasetByIdUseCase, {
  execute: jest.fn(),
});

const $route = {
  path: "/dataset/ccc38de6-4241-4a92-97c1-31929b0575ca/annotation-mode",
  params: { id: "ccc38de6-4241-4a92-97c1-31929b0575ca" },
  query: {
    _page: 1,
    _status: "pending",
    _search: "",
  },
};

jest.mock("@/models/feedback-task-model/record/record.queries", () => ({
  RECORD_STATUS: {
    PENDING: "PENDING",
    DISCARDED: "DISCARDED",
    SUBMITTED: "SUBMITTED",
  },
  deleteAllRecords: () => {},
}));

describe("AnnotationModePage", () => {
  it("not render the layout while the data are in fetching state", () => {
    const options = {
      stubs: ["BaseModal", "DatasetTrainComponent", "BaseLoading"],
      mocks: {
        $route,
      },
    };

    jest
      .spyOn(useAnnotationModeViewModel, "useAnnotationModeViewModel")
      .mockReturnValue({
        isLoadingDataset: true,
      });

    const wrapper = shallowMount(AnnotationModePage, options);

    expect(wrapper.is(AnnotationModePage)).toBe(true);

    const headerComponentWrapper = wrapper.findComponent(
      HeaderAndTopAndOneColumn
    );

    expect(headerComponentWrapper.exists()).toBeFalsy();
  });
  it("render the layout when data are fetched and no error", () => {
    const options = {
      stubs: [
        "HeaderFeedbackTaskComponent",
        "SidebarFeedbackTaskComponent",
        "RecordFeedbackTaskAndQuestionnaireContent",
        "DatasetFiltersComponent",
        "PaginationFeedbackTaskComponent",
        "BaseModal",
        "DatasetTrainComponent",
        "BaseLoading",
      ],
      mocks: {
        $route,
      },
    };

    jest
      .spyOn(useAnnotationModeViewModel, "useAnnotationModeViewModel")
      .mockReturnValue({
        isLoadingDataset: false,
      });

    const wrapper = shallowMount(AnnotationModePage, options);

    expect(wrapper.is(AnnotationModePage)).toBe(true);
    const headerComponentWrapper = wrapper.findComponent(
      HeaderAndTopAndOneColumn
    );

    expect(headerComponentWrapper.exists()).toBeTruthy();
  });
});
