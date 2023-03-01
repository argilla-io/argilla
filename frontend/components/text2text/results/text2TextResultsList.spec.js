import { shallowMount } from "@vue/test-utils";
import Text2TextResultsListComponent from "./Text2TextResultsList";

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
      vectorId: ["text", "recognai.text2text-one-vector-v12", 13611426],
      vectorName: "text",
    },
  },
  recordId: 13611426,
  vector: {
    vectorId: ["text", "recognai.text2text-one-vector-v12", 13611426],
    vectorName: "text",
  },
};

// NOTE: the spy method need to be implemented before the mount/shallowMount
const spy = jest.spyOn(Text2TextResultsListComponent.methods, "searchRecords");

beforeEach(() => {
  wrapper = shallowMount(Text2TextResultsListComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("Text2TextResultsListComponent", () => {
  it("render the component and the child component", () => {
    expect(wrapper.is(Text2TextResultsListComponent)).toBe(true);
  });
  it("emit @search-records value from child emitted value", () => {
    wrapper
      .getComponent({
        ref: "text2textResultsListComponent",
      })
      .vm.$emit("search-records", emittedSearchRecord);

    expect(spy).toHaveBeenCalledWith(emittedSearchRecord);

    expect(wrapper.emitted("search-records")[0]).toStrictEqual([
      emittedSearchRecord,
    ]);
  });
});
