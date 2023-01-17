import { shallowMount } from "@vue/test-utils";
import ResultsComponent from "./Results";

let wrapper = null;
const options = {
  stubs: [
    "TextClassificationResultsList",
    "TokenClassificationResultsList",
    "Text2TextResultsList",
  ],
  propsData: {
    datasetId: ["owner", "name"],
    datasetTask: "TextClassification",
    datasetName: "name",
  },
};

beforeEach(() => {
  wrapper = shallowMount(ResultsComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("ResultsComponent", () => {
  it("render the component", async () => {
    expect(wrapper.is(ResultsComponent)).toBe(true);
  });
  it("render TextClassificationResultsList if task is TextClassification", async () => {
    await isCorrectChildComponentIsRendered("TextClassification");
  });
  it("render TokenClassificationResultsList if task is TokenClassification", async () => {
    await isCorrectChildComponentIsRendered("TokenClassification");
  });
  it("render TextClassificationResultsList if task is TextClassification", async () => {
    await isCorrectChildComponentIsRendered("TextClassification");
  });
});

const isCorrectChildComponentIsRendered = async (datasetTask) => {
  await wrapper.setProps({ datasetTask: `${datasetTask}` });
  const childComponentToRender = wrapper.vm.currentTaskResultsList;
  expect(childComponentToRender).toBe(`${datasetTask}ResultsList`);
};
