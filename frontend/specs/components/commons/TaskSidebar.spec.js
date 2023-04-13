import { shallowMount } from "@vue/test-utils";
import TaskSidebar from "@/components/commons/sidebar/TaskSidebar.component";
import { SIDEBAR_ITEMS } from "@/components/commons/sidebar/sidebarItems.config";

jest.mock("@/models/dataset.utilities", () => ({
  getDatasetFromORM: () => ({
    $id: "settings_textclass_no_labels",
    id: "settings_textclass_no_labels",
    name: "settings_textclass_no_labels",
  }),
  getDatasetTaskById: () => "text-classification",
}));
jest.mock("@/models/viewSettings.queries", () => ({
  getViewSettingsByDatasetName: () => ({
    viewMode: "annotation",
  }),
}));
jest.mock("@/models/Dataset", () => ({
  getDatasetModelPrimaryKey: () => ({
    name: "settings_textclass_no_labels",
    workspace: "recognai",
  }),
}));
const $route = {
  params: {
    workspace: "recognai",
    dataset: "dataset_name",
  },
};

function mountSidebar() {
  return shallowMount(TaskSidebar, {
    stubs: ["SidebarMenu", "SidebarPanel"],
    propsData: {
      currentMetric: undefined,
      sidebarItems: SIDEBAR_ITEMS["TEXT_CLASSIFICATION"],
    },
    mocks: {
      $route,
    },
  });
}

describe("TaskSidebar", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test.skip("Required property", () => {
    shallowMount(TaskSidebar);
    expect(spy).toBeCalledWith(
      expect.stringContaining('[Vue warn]: Missing required prop: "dataset"')
    );
  });

  test("renders properly", () => {
    const wrapper = mountSidebar();
    expect(wrapper).toMatchSnapshot();
  });

  test("Show sidebar panel", async () => {
    const wrapper = mountSidebar();
    await wrapper.setData({ sidebarVisible: true });
    expect(wrapper).toMatchSnapshot();
  });
});
