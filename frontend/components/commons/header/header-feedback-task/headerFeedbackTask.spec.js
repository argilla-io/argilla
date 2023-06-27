import { shallowMount } from "@vue/test-utils";
import HeaderFeedbackTask from "./HeaderFeedbackTask.component";

let wrapper = null;
const options = {
  stubs: [
    "BaseTopbarBrand",
    "BaseBreadcrumbs",
    "BaseButton",
    "DatasetSettingsIconFeedbackTaskComponent",
    "User",
    "NuxtLink",
  ],
  mocks: {
    $auth: {
      user: {
        role: "admin",
      },
    },
  },
  propsData: {
    breadcrumbs: [
      { link: { name: "datasets" }, name: "Home" },
      { link: { path: "/datasets?workspace=recognai" }, name: "recognai" },
      {
        link: {
          name: null,
          params: {
            workspace: "recognai",
            dataset: "imdb-single-label-all-records",
          },
        },
        name: "imdb-single-label-all-records",
      },
    ],
    datasetId: "65931567-0b51-4e74-9aff-834c32a3d898",
    showTrainButton: true,
  },
};

beforeEach(() => {
  wrapper = shallowMount(HeaderFeedbackTask, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("HeaderFeedbackTask", () => {
  it("render the component", () => {
    expect(wrapper.is(HeaderFeedbackTask)).toBe(true);
  });
  it("render Train button if user role is admin", () => {
    expect(wrapper.findComponent({ ref: "trainButtonRef" }).exists()).toBe(
      true
    );
  });
  it("render Train button if user role is owner", () => {
    const wrapper = shallowMount(HeaderFeedbackTask, {
      ...options,
      mocks: {
        $auth: {
          user: {
            role: "owner",
          },
        },
      },
    });
    expect(wrapper.findComponent({ ref: "trainButtonRef" }).exists()).toBe(
      true
    );
  });
  it("Don't render Train button if user role is not admin or owner", () => {
    const wrapper = shallowMount(HeaderFeedbackTask, {
      ...options,
      mocks: {
        $auth: {
          user: {
            role: "annotator",
          },
        },
      },
    });
    expect(wrapper.findComponent({ ref: "trainButtonRef" }).exists()).toBe(
      false
    );
  });
});
