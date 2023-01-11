import { shallowMount } from "@vue/test-utils";
import SimilarityRecordReference from "./SimilarityRecordReference.component";
import { TextClassificationRecord } from "@/models/TextClassification";

let wrapper = null;
const options = {
  slots: {
    default: "Record Content",
  },
  propsData: {
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
  it("expect to render the content in the slot", async () => {
    expect(wrapper.html()).toContain("Record Content");
  });
});
