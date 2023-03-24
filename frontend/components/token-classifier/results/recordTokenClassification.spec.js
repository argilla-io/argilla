import { shallowMount } from "@vue/test-utils";
import RecordTokenClassificationComponent from "./RecordTokenClassification";
import "@/plugins/filters";

jest.mock("@/models/globalLabel.queries", () => ({
  getAllLabelsByDatasetId: () => [
    {
      $id: "['A','recognai.new-dataset-with-settings-fo-token']",
      color_id: 1,
      dataset_id: "recognai.new-dataset-with-settings-fo-token",
      id: "A",
      is_activate: false,
      is_saved_in_back: false,
      order: 1,
      shortcut: "2",
      text: "A",
    },
  ],
}));

let wrapper = null;
const options = {
  mocks: {
    $keywordsSpans: () => [],
  },
  stubs: ["text-spans", "record-action-buttons"],
  propsData: {
    datasetId: ["recognai", "new-dataset-with-settings-fo-token"],
    datasetName: "new-dataset-with-settings-fo-token",
    datasetQuery: {
      annotated_as: undefined,
      annotated_by: undefined,
      from: undefined,
      limit: undefined,
      metadata: undefined,
      predicted: undefined,
      predicted_as: undefined,
      predicted_by: undefined,
      query_text: undefined,
      score: undefined,
      status: undefined,
      text: undefined,
    },
    datasetLastSelectedEntity: {},
    viewSettings: {
      $id: "new-dataset-with-settings-fo-token",
      arePendingRecords: false,
      headerHeight: 222,
      id: "new-dataset-with-settings-fo-token",
      loading: false,
      pagination: {},
      shortcut_chars: "1234567890QWERTYUIOPASDFGHJKLZXCVBNM",
      viewMode: "annotate",
      visibleMetrics: false,
      visibleRulesList: false,
    },
    record: {
      annotatedEntities: [],
      annotation: {},
      event_timestamp: "2023-02-23T16:11:57.010883",
      id: "38d6aacf-1ef9-4c7c-b12d-82972298ba92",
      last_updated: "2023-03-14T23:35:55.104685",
      metadata: {},
      originStatus: "Discarded",
      prediction: undefined,
      search_keywords: [],
      selected: false,
      status: "Discarded",
      text: "Test example",
      tokens: [],
      vectors: {},
    },
  },
};

beforeEach(() => {
  wrapper = shallowMount(RecordTokenClassificationComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RecordTokenClassificationComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(RecordTokenClassificationComponent)).toBe(true);
  });
  it("not render img tag if metadata does not contains the URL", () => {
    expect(wrapper.find(".record--image-area").exists()).toBe(false);
  });
  it("render the image in the record if metadata contains the URL", async () => {
    await wrapper.setProps({
      record: {
        annotatedEntities: [],
        annotation: {},
        event_timestamp: "2023-02-23T16:11:57.010883",
        id: "38d6aacf-1ef9-4c7c-b12d-82972298ba92",
        last_updated: "2023-03-14T23:35:55.104685",
        metadata: { _image_url: "https://robohash.org/0.png" },
        originStatus: "Discarded",
        prediction: undefined,
        search_keywords: [],
        selected: false,
        status: "Discarded",
        text: "Test example",
        tokens: [],
        vectors: {},
      },
    });

    expect(wrapper.find(".record--image-area").exists()).toBe(true);
    expect(wrapper.find(".record--image-area>img").attributes("src")).toBe(
      "https://robohash.org/0.png"
    );
  });
});
