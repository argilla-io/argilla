import { shallowMount } from "@vue/test-utils";
import RecordTextClassificationComponent from "./RecordTextClassification";

let wrapper = null;
const options = {
  stubs: ["record-inputs", "classifier-exploration-area", "base-tag"],
  propsData: {
    viewSettings: {},
    datasetId: ["workspace", "name"],
    datasetName: "name",
    datasetLabels: ["label 1", "label 2"],
    record: {
      id: "00171137-272c-43d0-a8e8-d05f7ed8eb49",
      metadata: {},
      annotation: {
        agent: "recognai",
        labels: [{ class: "card_arrival", score: 1 }],
      },
      status: "Validated",
      selected: false,
      event_timestamp: "2022-12-22T11:11:28.214440",
      vectors: {},
      last_updated: "2023-01-17T11:03:30.613183",
      search_keywords: [],
      inputs: {
        text: "I made a deposit this morning but it is still pending?",
      },
      multi_label: false,
    },
    isMultiLabel: false,
    isReferenceRecord: false,
  },
};

beforeEach(() => {
  wrapper = shallowMount(RecordTextClassificationComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RecordTextClassificationComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(RecordTextClassificationComponent)).toBe(true);
  });
  it("not render img tag if metadata does not contains the URL", () => {
    expect(wrapper.find(".record--image-area").exists()).toBe(false);
  });
  it("render the image in the record if metadata contains the URL", async () => {
    await wrapper.setProps({
      record: {
        id: "00171137-272c-43d0-a8e8-d05f7ed8eb49",
        metadata: { _image_url: "https://robohash.org/0.png" },
        annotation: {
          agent: "recognai",
          labels: [{ class: "card_arrival", score: 1 }],
        },
        status: "Validated",
        selected: false,
        event_timestamp: "2022-12-22T11:11:28.214440",
        vectors: {},
        last_updated: "2023-01-17T11:03:30.613183",
        search_keywords: [],
        inputs: {
          text: "I made a deposit this morning but it is still pending?",
        },
        multi_label: false,
      },
    });

    expect(wrapper.find(".record--image-area").exists()).toBe(true);
    expect(wrapper.find(".record--image-area>img").attributes("src")).toBe(
      "https://robohash.org/0.png"
    );
  });
});
