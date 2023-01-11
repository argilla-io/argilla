import { mount } from "@vue/test-utils";
import Component from "@/components/text-classifier/results/RecordTextClassification";

import { TextClassificationRecord } from "@/models/TextClassification";

const $route = {
  query: {},
};

const props = {
  record: new TextClassificationRecord({
    annotation: {
      agent: "recognai",
      labels: [{ class: "Test", score: 1 }],
    },
    inputs: {
      text: "My text",
    },
    multi_label: false,
    prediction: {
      agent: "test",
      labels: [
        { class: "Test", score: 0.6 },
        { class: "A", score: 0.4 },
        { class: "B", score: 0.2 },
      ],
    },
  }),
  dataset: {
    task: "TextClassification",
    query: {
      text: "mock test",
    },
    isMultiLabel: false,
    viewSettings: {
      viewMode: "explore",
    },
    labels: ["Test", "A", "B"],
  },
};

function mountComponent() {
  return mount(Component, {
    propsData: props,
    mocks: {
      $route,
    },
  });
}

describe("RecordTextClassification", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test.skip("Required property", () => {
    expect(() => {
      mount(Component);
      expect(spy).toBeCalledWith(
        expect.stringContaining('[Vue warn]: Missing required prop: "dataset"')
      );
    }).toThrowError(TypeError);
  });

  test.skip("renders properly", () => {
    const wrapper = mountComponent();
    expect(wrapper).toMatchSnapshot();
  });

  test.skip("renders with empty prediction correctly", () => {
    const wrapper = mount(Component, {
      propsData: {
        ...props,
        record: {
          prediction: {},
        },
      },
    });
    expect(wrapper).toMatchSnapshot();
  });
});
