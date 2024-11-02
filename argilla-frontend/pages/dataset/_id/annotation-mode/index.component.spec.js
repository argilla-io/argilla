import { shallowMount } from "@vue/test-utils";
import AnnotationModePage from "./index";
import AnnotationPage from "@/layouts/AnnotationPage";
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

describe("AnnotationModePage", () => {
  it("render the layout while the data are in fetching state", () => {
    const options = {
      stubs: [
        "HeaderFeedbackTask",
        "SidebarFeedbackTaskContainer",
        "RecordFeedbackTaskAndQuestionnaire",
        "DatasetFilters",
        "PaginationFeedbackTask",
        "BaseModal",
        "BaseLoading",
        "PersistentStorageBanner",
      ],
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

    const headerComponentWrapper = wrapper.findComponent(AnnotationPage);

    expect(headerComponentWrapper.exists()).toBeTruthy();
  });
  it("render the layout when data are fetched and no error", () => {
    const options = {
      stubs: [
        "HeaderFeedbackTask",
        "SidebarFeedbackTaskContainer",
        "RecordFeedbackTaskAndQuestionnaire",
        "DatasetFilters",
        "PaginationFeedbackTask",
        "BaseModal",
        "BaseLoading",
        "PersistentStorageBanner",
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
    const headerComponentWrapper = wrapper.findComponent(AnnotationPage);

    expect(headerComponentWrapper.exists()).toBeTruthy();
  });
});
