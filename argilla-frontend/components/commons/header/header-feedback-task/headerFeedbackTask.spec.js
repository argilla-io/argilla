import { shallowMount } from "@vue/test-utils";
import HeaderFeedbackTask from "./HeaderFeedbackTask.component";
import * as useRole from "~/v1/infrastructure/services/useRole";

const options = {
  stubs: [
    "BaseTopbarBrand",
    "BaseBreadcrumbs",
    "BaseButton",
    "DatasetSettingsIconFeedbackTaskComponent",
    "UserAvatarTooltip",
    "NuxtLink",
  ],
  propsData: {
    breadcrumbs: [
      { link: { name: "datasets" }, name: "Home" },
      { link: { path: "/datasets?workspaces=recognai" }, name: "recognai" },
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

describe("HeaderFeedbackTask", () => {
  test("render the component", () => {
    jest.spyOn(useRole, "useRole").mockReturnValue({
      isAdminOrOwnerRole: true,
    });

    const wrapper = shallowMount(HeaderFeedbackTask, options);

    expect(wrapper.is(HeaderFeedbackTask)).toBeTruthy();
  });

  describe("Train button", () => {
    describe("show when", () => {
      test("render Train button if user role is admin or owner", () => {
        jest.spyOn(useRole, "useRole").mockReturnValue({
          isAdminOrOwnerRole: true,
        });

        const wrapper = shallowMount(HeaderFeedbackTask, options);

        expect(
          wrapper.findComponent({ ref: "trainButtonRef" }).exists()
        ).toBeTruthy();
      });
    });

    describe("hide when", () => {
      test("no render Train button if user role is not admin or owner", () => {
        jest.spyOn(useRole, "useRole").mockReturnValue({
          isAdminOrOwnerRole: false,
        });

        const wrapper = shallowMount(HeaderFeedbackTask, options);

        expect(
          wrapper.findComponent({ ref: "trainButtonRef" }).exists()
        ).toBeFalsy();
      });

      test("no render Train button if showTrainButton is false", () => {
        jest.spyOn(useRole, "useRole").mockReturnValue({
          isAdminOrOwnerRole: true,
        });

        const wrapper = shallowMount(HeaderFeedbackTask, {
          ...options,
          propsData: {
            ...options.propsData,
            showTrainButton: false,
          },
        });

        expect(
          wrapper.findComponent({ ref: "trainButtonRef" }).exists()
        ).toBeFalsy();
      });
    });
  });
});
