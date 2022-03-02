import { mount } from "@vue/test-utils";
import EntitiesSelector from "@/components/token-classifier/results/EntitiesSelector";

function mountEntitiesSelector() {
  return mount(EntitiesSelector, {
    propsData: {
      dataset: {
        task: "TextClassification",
        lastSelectedEntity: {
          colorId: 14,
          shortCut: "1",
          text: "Arreglo",
        },
        viewSettings: {
          annotationEnabled: false,
        },
        labels: ["A", "B"],
      },
      formattedEntities: [
        {
          colorId: 14,
          shortCut: "1",
          text: "Arreglo",
        },
        {
          colorId: 1,
          shortCut: "2",
          text: "CARDINAL",
        },
      ],
      token: {
        end: 73,
        entity: {
          end: 73,
          end_token: 15,
          label: "Arreglo",
          start: 57,
          start_token: 13,
        },
        origin: "annotation",
      },
      showEntitiesSelector: true,
      suggestedLabel: "GPE",
    },
  });
}

describe("EntitiesSelector", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountEntitiesSelector();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
