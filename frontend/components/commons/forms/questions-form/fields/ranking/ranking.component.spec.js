import { shallowMount } from "@vue/test-utils";
import RankingComponent from "./Ranking.component";

let wrapper = null;

const options = {
  stubs: ["QuestionHeaderComponent"],
  propsData: {
    title: "This is the title",
    settings: {},
  },
};

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
  it("has a title prop as required and must be a string", () => {
    expect(RankingComponent.props.title).toMatchObject({
      type: String,
      required: true,
    });
  });
  it("has a isRequired prop with a default value and must be a boolean", () => {
    expect(RankingComponent.props.isRequired).toMatchObject({
      type: Boolean,
      default: false,
    });
  });
  it("has a description prop with a default value and must be a string", () => {
    expect(RankingComponent.props.description).toMatchObject({
      type: String,
      default: "",
    });
  });
  it("has a settings prop with as required and must be an object", () => {
    expect(RankingComponent.props.settings).toMatchObject({
      type: Object,
      required: true,
    });
  });
});
