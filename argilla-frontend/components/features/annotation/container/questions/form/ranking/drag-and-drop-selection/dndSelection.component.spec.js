import { shallowMount } from "@vue/test-utils";
import DndSelectionComponent from "./DndSelection.component";
import { adaptQuestionsToSlots } from "../ranking-adapter";
import { settingsFake, settingsFakeWith12Elements } from "../ranking-fakes";

let wrapper = null;
const options = {
  stubs: ["draggable", "BaseTooltip"],
  propsData: { ranking: {} },
};

const eventFor = (key) => {
  return { stopPropagation: jest.fn(), key };
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
});

describe("rankWithKeyboard should", () => {
  it("no move question because the user press non existing slot for a key", () => {
    const ranking = adaptQuestionsToSlots(settingsFake);
    const questionOne = ranking.questions[0];
    const component = shallowMount(DndSelectionComponent, {
      ...options,
      propsData: { ranking },
    });

    component.vm.rankWithKeyboard(eventFor("5"), questionOne);

    expect(component.vm.ranking.slots[0].items.length).toBeFalsy();
    expect(component.vm.ranking.slots[1].items.length).toBeFalsy();
    expect(component.vm.ranking.slots[2].items.length).toBeFalsy();
    expect(component.vm.ranking.slots[3].items.length).toBeFalsy();
  });

  it("no move question because the user press invalid key", () => {
    const ranking = adaptQuestionsToSlots(settingsFake);
    const questionOne = ranking.questions[0];
    const component = shallowMount(DndSelectionComponent, {
      ...options,
      propsData: { ranking },
    });

    component.vm.rankWithKeyboard(eventFor("&"), questionOne);

    expect(component.vm.ranking.slots[0].items.length).toBeFalsy();
    expect(component.vm.ranking.slots[1].items.length).toBeFalsy();
    expect(component.vm.ranking.slots[2].items.length).toBeFalsy();
    expect(component.vm.ranking.slots[3].items.length).toBeFalsy();
  });

  it("move correctly question when user press 1", async () => {
    const ranking = adaptQuestionsToSlots(settingsFake);
    const questionOne = ranking.questions[0];
    const component = shallowMount(DndSelectionComponent, {
      ...options,
      propsData: { ranking },
    });

    component.vm.rankWithKeyboard(eventFor("1"), questionOne);

    expect(component.vm.ranking.slots[0].items[0]).toBe(questionOne);
  });

  it("prevent duplicate question if user try to move twice the same question", () => {
    const ranking = adaptQuestionsToSlots(settingsFake);
    const questionOne = ranking.questions[0];
    const component = shallowMount(DndSelectionComponent, {
      ...options,
      propsData: { ranking },
    });
    component.vm.rankWithKeyboard(eventFor("1"), questionOne);

    component.vm.rankWithKeyboard(eventFor("1"), questionOne);

    expect(component.vm.ranking.slots[0].items[0]).toBe(questionOne);
    expect(component.vm.ranking.slots[0].items.length).toBe(1);
    expect(component.vm.ranking.questions.length).toBe(3);
  });

  it("move a question from any slot to other one", async () => {
    const ranking = adaptQuestionsToSlots(settingsFake);
    const questionOne = ranking.questions[0];
    const component = shallowMount(DndSelectionComponent, {
      ...options,
      propsData: { ranking },
    });
    component.vm.rankWithKeyboard(eventFor("2"), questionOne);

    await new Promise((res) => {
      setTimeout(() => {
        res();
      }, 400);
    });

    component.vm.rankWithKeyboard(eventFor("1"), questionOne);

    expect(component.vm.ranking.slots[0].items[0]).toBe(questionOne);
    expect(component.vm.ranking.slots[0].items.length).toBe(1);
    expect(component.vm.ranking.questions.length).toBe(3);
    expect(component.vm.ranking.slots[1].items.length).toBe(0);
  });

  it("move a question to slot number 11", async () => {
    const ranking = adaptQuestionsToSlots(settingsFakeWith12Elements);
    const questionOne = ranking.questions[0];
    const component = shallowMount(DndSelectionComponent, {
      ...options,
      propsData: { ranking },
    });

    component.vm.rankWithKeyboard(eventFor("1"), questionOne);
    component.vm.rankWithKeyboard(eventFor("1"), questionOne);

    expect(component.vm.ranking.slots[10].items.length).toBe(1);
    expect(component.vm.ranking.slots[10].items[0]).toBe(questionOne);
    expect(component.vm.ranking.questions.length).toBe(11);
  });
});
