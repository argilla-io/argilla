import { mount } from "@vue/test-utils";
import BaseDateVue from "./BaseDate.vue";

class DateMocked extends Date {
  constructor(args) {
    super(args);
  }

  getTimezoneOffset(): number {
    return -120;
  }
}

const dateMocked = new DateMocked("2023-07-19");
jest.useFakeTimers().setSystemTime(dateMocked);

describe("Base Date should", () => {
  test("should format date correctly", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-07-19").toString(),
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 hours ago", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-07-18 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day as yesterday", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-07-17 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 days ago", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-07-16 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day last week", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-07-11 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 weeks ago", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-07-01 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day last month", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-06-18 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });

  test("should format day 2 months ago", () => {
    const baseDate = mount(BaseDateVue, {
      propsData: {
        date: new Date("2023-05-18 22:00").toString(),
        format: "date-relative-now",
      },
    });

    expect(baseDate).toMatchSnapshot();
  });
});
