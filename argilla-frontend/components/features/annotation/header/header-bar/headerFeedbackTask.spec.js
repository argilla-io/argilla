import { shallowMount } from "@vue/test-utils";
import HeaderFeedbackTask from "./HeaderFeedbackTask";
import * as useRole from "~/v1/infrastructure/services/useRole";

const options = {
  stubs: [
    "BaseTopbarBrand",
    "BaseBreadcrumbs",
    "BaseButton",
    "DatasetSettingsIconFeedbackTask",
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
});
