import { shallowMount } from "@vue/test-utils";
import RankingComponent from "./Ranking.component";

let wrapper = null;

const options = {};

beforeEach(() => {
  wrapper = shallowMount(RankingComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RankingComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(RankingComponent)).toBe(true);

    const QuestionHeaderWrapper = wrapper.findComponent({
      name: "QuestionHeaderComponent",
    });

    expect(QuestionHeaderWrapper.exists()).toBe(true);
  });
});
