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
  it("has a listOfItems prop as required and must be an array", () => {
    expect(DndSelectionComponent.props.listOfItems).toMatchObject({
      type: Array,
      required: true,
    });
  });
});
