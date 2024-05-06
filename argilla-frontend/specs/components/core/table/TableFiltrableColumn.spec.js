import { mount } from "@vue/test-utils";
import TableFiltrableColumn from "@/components/base/base-table/TableFiltrableColumn";

function mountTableFiltrableColumn() {
  return mount(TableFiltrableColumn, {
    propsData: {
      filters: {
        workspace: ["recognai"],
      },
      column: {
        class: "text",
        field: "workspace",
        filtrable: "true",
        name: "Workspace",
        type: "text",
      },
      data: [
        {
          name: "dataset_1",
          workspace: "recognai",
          task: "TokenClassification",
        },
      ],
    },
  });
}

describe("TableFiltrableColumn", () => {
  const spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountTableFiltrableColumn();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
