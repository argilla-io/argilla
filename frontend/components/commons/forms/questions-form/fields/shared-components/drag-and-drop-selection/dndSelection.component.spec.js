import { shallowMount } from "@vue/test-utils";
import DndSelectionComponent from "./DndSelection.component";
import { adaptQuestionsToSlots } from "../../ranking/ranking-adapter";
import { settingsFake } from "../../ranking/ranking-fakes";

let wrapper = null;
const options = {
  stubs: ["draggable"],
  propsData: { ranking: {} },
};

beforeEach(() => {
  wrapper = shallowMount(DndSelectionComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("DndSelectionComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(DndSelectionComponent)).toBe(true);
  });
  it("has a ranking prop as required and must be an Object", () => {
    expect(DndSelectionComponent.props.ranking).toMatchObject({
      type: Object,
      required: true,
    });
  });
  it("rankWithKeyboard", () => {
    const ranking = adaptQuestionsToSlots(settingsFake);
    const questionOne = ranking.questions[0];
    const component = shallowMount(DndSelectionComponent, {
      ...options,
      propsData: { ranking },
    });
    component.vm.rankWithKeyboard({ key: "1" }, questionOne);
    expect(component.vm.ranking.slots[0].items[0]).toBe(questionOne);
  });
});
