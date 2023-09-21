import { shallowMount } from "@vue/test-utils";
import TokenClassificationResultsListComponent from "./TokenClassificationResultsList";

let wrapper = null;
const options = {
  stubs: ["results-list"],
  propsData: {
    datasetId: ["workspace", "name"],
    datasetTask: "TextClassification",
  },
};

const emittedSearchRecord = {
  query: {
    vector: {
      vectorId: [
        "mini-lm-sentence-transformers",
        "recognai.tok-c-ner-vectors-v12",
        3171,
      ],
      vectorName: "mini-lm-sentence-transformers",
    },
  },
  recordId: 3171,
  vector: {
    vectorId: [
      "mini-lm-sentence-transformers",
      "recognai.tok-c-ner-vectors-v12",
      3171,
    ],
    vectorName: "mini-lm-sentence-transformers",
  },
};

// NOTE: the spy method need to be implemented before the mount/shallowMount
const spy = jest.spyOn(
  TokenClassificationResultsListComponent.methods,
  "searchRecords"
);

beforeEach(() => {
  wrapper = shallowMount(TokenClassificationResultsListComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("TokenClassificationResultsListComponent", () => {
  it("render the component and the child component", () => {
    expect(wrapper.is(TokenClassificationResultsListComponent)).toBe(true);
  });
  it("emit @search-records value from child emitted value", () => {
    wrapper
      .getComponent({
        ref: "tokenClassificationResultsListComponent",
      })
      .vm.$emit("search-records", emittedSearchRecord);

    expect(spy).toHaveBeenCalledWith(emittedSearchRecord);

    expect(wrapper.emitted("search-records")[0]).toStrictEqual([
      emittedSearchRecord,
    ]);
  });
});
