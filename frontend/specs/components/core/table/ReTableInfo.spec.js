import { mount } from "@vue/test-utils";
import ReTableInfo from "@/components/core/table/ReTableInfo";

const $route = {
  query: {},
};

function mountReTableInfo() {
  return mount(ReTableInfo, {
    propsData: {
      actions: [],
      columns: [
        {
          class: "text",
          field: "owner",
          filtrable: "true",
          name: "Workspace",
          type: "text",
        },
      ],
      data: [
        {
          name: "dataset_1",
          owner: "recognai",
          task: "TokenClassification",
        },
        {
          name: "dataset_2",
          owner: "recognai",
          task: "TokenClassification",
        },
      ],
      deleteModalContent: {
        text: "You are about to delete: <strong>undefined</strong>. This action cannot be undone",
        title: "Delete confirmation",
      },
      emptySearchInfo: {
        title: "0 datasets found",
      },
      globalActions: false,
      groupBy: undefined,
      hideButton: false,
      noDataInfo: undefined,
      querySearch: undefined,
      filterFromRoute: "owner",
      searchOn: "name",
      sortedByField: "last_updated",
      sortedOrder: "desc",
      visibleModalId: undefined,
    },
    mocks: {
      $route,
    },
  });
}

describe("ReTableInfo", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountReTableInfo();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
