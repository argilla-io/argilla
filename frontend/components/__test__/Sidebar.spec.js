
import { shallowMount } from "@vue/test-utils";
import Sidebar from "../commons/sidebar/Sidebar";


const factory = () => {
  return shallowMount(Sidebar, {
  });
};

describe("Sidebar", () => {
  // test("mounts properly", () => {
  //   const wrapper = factory();
  //   expect(wrapper.isVueInstance()).toBeTruthy();
  // });

  test("renders properly", () => {
    const wrapper = shallowMount(Sidebar, {
      mocks: {
        $auth: {
          loggedIn: true,
        },
        $config: {
          securityEnabled: true,
        }
      },
    });
    expect(wrapper.html()).toMatchSnapshot();
  });
});