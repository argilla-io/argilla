import { mount } from "@vue/test-utils";
import TableFiltrableColumn from "@/components/base/table/TableFiltrableColumn";

function mountTableFiltrableColumn() {
  return mount(TableFiltrableColumn, {
    propsData: {
      filters: {
        owner: ["recognai"],
      },
      column: {
        class: "text",
        field: "owner",
        filtrable: "true",
        name: "Workspace",
        type: "text",
      },
      data: [
        {
          name: "dataset_1",
          owner: "recognai",
          task: "TokenClassification",
        },
      ],
    },
  });
}

describe("TableFiltrableColumn", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountTableFiltrableColumn();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
