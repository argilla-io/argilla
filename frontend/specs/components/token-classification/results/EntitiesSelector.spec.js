import { mount } from "@vue/test-utils";
import EntitiesSelector from "@/components/token-classifier/results/EntitiesSelector";
const $entitiesMaxColors = 50;

function mountEntitiesSelector() {
  return mount(EntitiesSelector, {
    propsData: {
      datasetId: ["name", "owner"],
      datasetLastSelectedEntity: {
        colorId: 14,
        shortCut: "1",
        text: "Arreglo",
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
    mocks: {
      $entitiesMaxColors,
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
