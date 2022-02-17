import { mount } from "@vue/test-utils";
import ResultsTitle from "@/components/commons/results/ResultsTitle";

function mountResultsTitle() {
  return mount(ResultsTitle, {
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

describe("ResultsTitle", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountResultsTitle();
    expect(wrapper).toMatchSnapshot();
  });
});
