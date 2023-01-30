import { shallowMount } from "@vue/test-utils";
import HelpInfo from "./HelpInfo";

let wrapper = null;

const options = {
  stubs: ["HelpInfoContent"],
  modalVisible: false,
  similarity: {
    id: "similarity",
    name: "Similarity Search",
    component: "helpInfoSimilarity",
  },
  explain: {
    id: "explain",
    name: "Colors in token attributions",
    component: "helpInfoExplain",
  },
  propsData: {
    datasetId: ["owner", "name"],
    datasetTask: "TextClassification",
    datasetName: "name",
  },
};
beforeEach(() => {
  wrapper = shallowMount(HelpInfo, options);
});
afterEach(() => {
  wrapper.destroy();
});

describe("HelpInfoComponent", () => {
  it.skip("render the component", () => {
    expect(wrapper.is(HelpInfo)).toBe(true);
  });
  it.skip("method showHelpModal should toggle visibleModal to true", async () => {
    wrapper.vm.showHelpModal();
    expect(wrapper.vm.modalVisible).toBe(true);
  });
  it.skip("method showHelpModal should toggle visibleModal to false", async () => {
    await wrapper.setData({ modalVisible: true });
    wrapper.vm.showHelpModal();
    expect(wrapper.vm.modalVisible).toBe(false);
  });
});
