import { shallowMount } from "@vue/test-utils";
import Login from "./login.vue";

const stubs = ["BaseLoading", "brand-logo", "geometric-shape-a", "base-button"];

const validAuthToken = btoa("USERNAME:PASSWORD");

describe("Login page should", () => {
  it("still in the same page if the auth token is not valid", () => {
    const loginUserSpy = jest.spyOn(Login.methods, "loginUser");

    shallowMount(Login, {
      mocks: {
        $route: {
          query: {
            auth: "INVALID",
          },
        },
      },
    });

    expect(loginUserSpy).toHaveBeenCalledTimes(0);
  });

  it("still in the same page if the auth token query params is empty", () => {
    const loginUserSpy = jest.spyOn(Login.methods, "loginUser");

    shallowMount(Login, {
      mocks: {
        $route: {
          query: {},
        },
      },
    });

    expect(loginUserSpy).toHaveBeenCalledTimes(0);
  });

  it("try to login user when the auth token is valid", () => {
    const loginUserSpy = jest.spyOn(Login.methods, "loginUser");

    shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth: validAuthToken,
          },
        },
      },
    });

    expect(loginUserSpy).toHaveBeenCalledTimes(1);
  });

  it("the auth token is valid when the object has the username and password", () => {
    const wrapper = shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth: validAuthToken,
          },
        },
      },
    });

    expect(wrapper.vm.hasAuthToken).toBeTruthy();
  });

  it("the auth token is not valid when the object has username but no password", () => {
    const auth = btoa("USERNAME:");

    const wrapper = shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth,
          },
        },
      },
    });

    expect(wrapper.vm.hasAuthToken).toBeFalsy();
  });

  it("the auth token is not valid when the object has no username but password", () => {
    const auth = btoa(":PASSWORD");

    const wrapper = shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth,
          },
        },
      },
    });

    expect(wrapper.vm.hasAuthToken).toBeFalsy();
  });

  it("the auth token is not valid when the object has no username and no password", () => {
    const auth = btoa(":");

    const wrapper = shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth,
          },
        },
      },
    });

    expect(wrapper.vm.hasAuthToken).toBeFalsy();
  });

  it("the auth token is not valid when the object other object structure", () => {
    const auth = btoa("FOO");

    const wrapper = shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth,
          },
        },
      },
    });

    expect(wrapper.vm.hasAuthToken).toBeFalsy();
  });

  it("show the loading logo when the token is valid", () => {
    const wrapper = shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth: validAuthToken,
          },
        },
      },
    });

    const loadingLogo = wrapper.findComponent({
      name: "BaseLoading",
    });
    expect(loadingLogo.exists()).toBeTruthy();
  });

  it("no show the loading logo when the token is not valid", () => {
    const auth = "";

    const wrapper = shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth,
          },
        },
      },
    });

    const loadingLogo = wrapper.findComponent({
      name: "BaseLoading",
    });
    expect(loadingLogo.exists()).toBeFalsy();
  });
});
