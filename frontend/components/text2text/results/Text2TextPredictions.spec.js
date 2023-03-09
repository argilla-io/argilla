import { shallowMount } from "@vue/test-utils";
import Text2TextPredictionsComponent from "./Text2TextPredictions";

let wrapper = null;

const options = {
  stubs: ["base-button"],
  idState() {
    return {
      arePredictionsVisible: false,
      selectedPredictionIndex: 0,
    };
  },
  propsData: {
    record: {
      id: 13611370,
    },
    predictions: [
      {
        score: 0.32,
        text: "text 1",
      },
      {
        score: 1,
        text: "text 2",
      },
    ],
  },
};

beforeEach(() => {
  wrapper = shallowMount(Text2TextPredictionsComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("Text2TextPredictionsComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(Text2TextPredictionsComponent)).toBe(true);
  });
});
