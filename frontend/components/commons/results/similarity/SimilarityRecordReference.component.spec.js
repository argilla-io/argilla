import { shallowMount } from "@vue/test-utils";
import SimilarityRecordReference from "./SimilarityRecordReference.component";
import { TextClassificationRecord } from "@/models/TextClassification";

let wrapper = null;
const options = {
  stubs: ["nuxt", "results-record"],
  propsData: {
    datasetId: ["owner", "name"],
    datasetTask: "TextClassification",
    dataset: {
      type: Object,
      viewSettings: {
        annotationEnabled: false,
      },
    },
    referenceRecord: new TextClassificationRecord({
      inputs: { text: "My text" },
    }),
  },
};
beforeEach(() => {
  wrapper = shallowMount(SimilarityRecordReference, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("SimilarityRecordReferenceComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(SimilarityRecordReference)).toBe(true);
  });
  it("expect to have record--reference class", async () => {
    expect(wrapper.find(".record--reference").exists()).toBe(true);
  });
});
