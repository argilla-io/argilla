import { shallowMount } from "@vue/test-utils";
import TaskSearchComponent from "./TaskSearch";

let wrapper = null;
const options = {
  stubs: ["results"],
  propsData: {
    datasetId: ["owner", "name"],
    datasetTask: "TextClassification",
    datasetName: "name",
  },
};

beforeEach(() => {
  wrapper = shallowMount(TaskSearchComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("TaskSearchComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(TaskSearchComponent)).toBe(true);
  });
});
