import { mount } from "@vue/test-utils";
import BaseDateVue from "./BaseDate.vue";
import "vue-i18n";

const mocks = {
  $i18n: {
    locale: "en",
  },
};

const dateMocked = new Date("2023-07-19 00:00:00");
jest.useFakeTimers("modern").setSystemTime(dateMocked);
jest.mock("vue-i18n");

describe("Base Date should", () => {
  test("should format date correctly", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-07-19").toString(),
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 1 second ago", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-07-18 23:59:59").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 seconds ago", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-07-18 23:59:58").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 hours ago", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-07-18 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day as yesterday", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-07-17 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 days ago", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-07-16 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day last week", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-07-11 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 weeks ago", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-07-01 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day last month", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-06-18 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 months ago", () => {
    const baseDate = mount(BaseDateVue, {
      mocks: {
        $i18n: {
          locale: "en",
        },
      },
      propsData: {
        date: new Date("2023-05-18 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });
});
