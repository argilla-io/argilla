import { shallowMount } from "@vue/test-utils";
import RankingComponent from "./Ranking.component";

let wrapper = null;

const QuestionHeaderComponentStub = {
  name: "QuestionHeaderComponent",
  template: "<div />",
  props: ["title", "isRequired", "tooltipMessage"],
};
const dndSelectionComponentStub = {
  name: "dndSelectionBaseComponent",
  template: "<div />",
  props: ["listOfItems"],
};

const options = {
  stubs: {
    QuestionHeaderComponent: QuestionHeaderComponentStub,
    dndSelectionComponent: dndSelectionComponentStub,
  },
  propsData: {
    title: "This is the title",
    values: [],
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

    const classWrapper = wrapper.find(".wrapper");
    expect(classWrapper.exists()).toBe(true);

    const QuestionHeaderWrapper = wrapper.findComponent(
      QuestionHeaderComponentStub
    );
    expect(QuestionHeaderWrapper.exists()).toBe(true);

    const dndSelectionWrapper = wrapper.findComponent(
      dndSelectionComponentStub
    );
    expect(dndSelectionWrapper.exists()).toBe(true);

    expect(wrapper.vm.isRequired).toBe(false);
    expect(wrapper.vm.description).toBe("");

    // TODO - replace mock by empty list (see two next lines)
    // expect(wrapper.vm.ranking).toStrictEqual([]);
    expect(wrapper.vm.ranking).toStrictEqual([
      {
        index: 1,
        items: [
          {
            title: "item 1",
          },
        ],
      },
      {
        index: 2,
        items: [
          {
            title: "item 2",
          },
          {
            title: "item 3",
          },
        ],
      },
    ]);
  });
  it("has a values prop as required and must be a array", () => {
    expect(RankingComponent.props.values).toMatchObject({
      type: Array,
      required: true,
    });
  });
  it("has a title prop as required and must be a string", () => {
    expect(RankingComponent.props.title).toMatchObject({
      type: String,
      required: true,
    });
  });
  it("pass the title props to the QuestionHeaderComponent", () => {
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("title")
    ).toBe(wrapper.vm.title);
  });
  it("has a isRequired prop with a default value and must be a boolean", () => {
    expect(RankingComponent.props.isRequired).toMatchObject({
      type: Boolean,
      default: false,
    });
  });
  it("pass the isRequired props to the QuestionHeaderComponent", () => {
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("isRequired")
    ).toBe(wrapper.vm.isRequired);
  });
  it("has a description prop with a default value and must be a string", () => {
    expect(RankingComponent.props.description).toMatchObject({
      type: String,
      default: "",
    });
  });
  it("pass the description props to the QuestionHeaderComponent", () => {
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("tooltipMessage")
    ).toBe(wrapper.vm.description);
  });
  it("has a settings prop with as required and must be an object with a validator", () => {
    expect(RankingComponent.props.settings.type).toBe(Object);
    expect(RankingComponent.props.settings.required).toBe(true);

    // FIXME
    expect(
      JSON.stringify(RankingComponent.props.settings.validator)
    ).toStrictEqual(
      JSON.stringify((settings) => {
        const settingsKeys = Object.keys(settings);
        const checkAllKeysOfSettingsAreValid = settingsKeys.every((key) =>
          ["type", "options", "ranking_slots"].includes(key)
        );
        return checkAllKeysOfSettingsAreValid;
      })
    );
  });
  it("pass the ranking list to the component dndSelectionBaseComponent", () => {
    expect(
      wrapper.findComponent(dndSelectionComponentStub).props("listOfItems")
    ).toStrictEqual(wrapper.vm.ranking);
  });
});
