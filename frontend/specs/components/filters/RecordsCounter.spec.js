import { mount } from "@vue/test-utils";
import RecordsCounter from "@/components/commons/header/filters/RecordsCounter";

function mountRecordsCounter() {
  return mount(RecordsCounter, {
    propsData: {
      dataset: {
        task: "TextClassification",
        results: {
          total: 400,
        },
        query: {
          annotated_as: undefined,
          annotated_by: undefined,
          from: undefined,
          limit: undefined,
          metadata: {},
          predicted: undefined,
          predicted_as: ["Alta"],
          predicted_by: undefined,
          score: undefined,
          status: undefined,
          text: "de",
        },
      },
      showWhenFiltered: true,
      excludedFilter: ["text"],
    },
  });
}

describe("RecordsCounter", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountRecordsCounter();
    expect(wrapper).toMatchSnapshot();
  });
});
