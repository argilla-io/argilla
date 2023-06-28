import { shallowMount } from "@vue/test-utils";
import RatingComponent from "./Rating.component";

const QuestionHeaderComponentStub = {
  name: "QuestionHeaderComponent",
  template: "<div />",
  props: ["title", "isRequired", "tooltipMessage"],
};
const RatingMonoSelectionComponentStub = {
  name: "RatingMonoSelectionComponent",
  template: "<div />",
  props: ["options"],
};

let wrapper = null;
const options = {
  stubs: {
    QuestionHeaderComponent: QuestionHeaderComponentStub,
    RatingMonoSelectionComponent: RatingMonoSelectionComponentStub,
  },
  propsData: {
    title: "This is the title",
    options: [
      { id: "helpfulness_reply_1_1", value: 1, text: 1, is_selected: false },
      { id: "helpfulness_reply_1_2", value: 2, text: 2, is_selected: false },
      { id: "helpfulness_reply_1_3", value: 3, text: 3, is_selected: false },
      { id: "helpfulness_reply_1_4", value: 4, text: 4, is_selected: false },
      { id: "helpfulness_reply_1_5", value: 5, text: 5, is_selected: false },
    ],
  },
};

beforeEach(() => {
  wrapper = shallowMount(RatingComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RatingComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(RatingComponent)).toBe(true);

    expect(wrapper.vm.isRequired).toBe(false);
    expect(wrapper.vm.description).toBe("");

    const QuestionHeaderWrapper = wrapper.findComponent(
      QuestionHeaderComponentStub
    );
    expect(QuestionHeaderWrapper.exists()).toBe(true);

    const RatingMonoSelectionWrapper = wrapper.findComponent(
      RatingMonoSelectionComponentStub
    );
    expect(RatingMonoSelectionWrapper.exists()).toBe(true);
  });
});
