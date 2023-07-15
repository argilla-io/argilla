import { shallowMount } from "@vue/test-utils";
import AnnotationModePage from "./index";
import HeaderAndTopAndOneColumn from "@/layouts/HeaderAndTopAndOneColumn";

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
      stubs: ["BaseModal", "DatasetTrainComponent"],
      mocks: {
        $route,
        $fetchState: {
          pending: true,
          error: null,
          timestamp: 1686579374810,
        },
      },
    };

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
        "CenterFeedbackTaskContent",
        "DatasetFiltersComponent",
        "PaginationFeedbackTaskComponent",
        "BaseModal",
        "DatasetTrainComponent",
      ],
      mocks: {
        $route,
        $fetchState: {
          pending: false,
          error: false,
          timestamp: 1686579374810,
        },
      },
    };

    const wrapper = shallowMount(AnnotationModePage, options);

    expect(wrapper.is(AnnotationModePage)).toBe(true);
    const headerComponentWrapper = wrapper.findComponent(
      HeaderAndTopAndOneColumn
    );

    expect(headerComponentWrapper.exists()).toBeTruthy();
  });
});
