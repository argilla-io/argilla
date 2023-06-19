import { shallowMount } from "@vue/test-utils";
import DndSelectionComponent from "./DndSelection.component";

let wrapper = null;
const options = {
  propsData: { listOfItems: [] },
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
