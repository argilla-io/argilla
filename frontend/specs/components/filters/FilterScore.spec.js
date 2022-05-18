import { mount } from "@vue/test-utils";
import FilterScore from "@/components/commons/header/filters/FilterScore";

function mountFilterScore() {
  return mount(FilterScore, {
    propsData: {
      filter: {
        key: "score",
        name: "Score",
        type: "score",
        group: "Predictions",
        id: "score",
        options: {
          "0.0-0.05": 38222,
          "0.05-0.1": 48,
          "0.1-0.15": 26,
          "0.15-0.2": 13,
          "0.2-0.25": 8,
          "0.25-0.3": 5,
          "0.3-0.35": 3,
          "0.35-0.4": 1,
          "0.4-0.45": 2,
          "0.45-0.5": 1,
          "0.5-0.55": 0,
          "0.55-0.6": 0,
          "0.6-0.65": 1,
          "0.65-0.7": 0,
          "0.7-0.75": 3,
          "0.75-0.8": 0,
          "0.8-0.85": 1,
          "0.85-0.9": 1,
          "0.9-0.95": 0,
          "0.95-1.0": 0,
          "1.0-*": 0,
        },
        selected: undefined,
        disabled: false,
      },
    },
  });
}

describe("FilterScore", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountFilterScore();
    expect(wrapper.html()).toMatchSnapshot();
  });

  test("Expand filter", async () => {
    const wrapper = mountFilterScore();
    await wrapper.setData({ scoreExpanded: true });
    expect(wrapper.html()).toMatchSnapshot();
  });
});
