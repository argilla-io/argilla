import { mount } from "@vue/test-utils";
import TaskSidebar from "@/components/commons/sidebar/TaskSidebar";

function mountSidebar() {
  return mount(TaskSidebar, {
    propsData: {
      dataset: {
        task: "TextClassification",
        viewSettings: {
          annotationEnabled: false,
        },
      },
    },
  });
}

describe("TaskSidebar", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("Required property", () => {
    mount(TaskSidebar);
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
