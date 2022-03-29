import { mount } from "@vue/test-utils";
import SortList from "@/components/commons/header/filters/SortList";

function mountSortList() {
  return mount(SortList, {
    propsData: {
      sort: [
        {
          disabled: false,
          group: "Predictions",
          id: "predicted_as",
          key: "predicted_as",
          name: "Predicted as",
          options: Object,
          order: "asc",
          placeholder: "Select labels",
          type: "select",
        },
      ],
      sortOptions: [
        {
          disabled: false,
          group: "Predictions",
          id: "predicted_as",
          key: "predicted_as",
          name: "Predicted as",
          options: Object,
          placeholder: "Select labels",
          selected: undefined,
          type: "select",
        },
      ],
    },
  });
}

describe("SortList", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountSortList();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
