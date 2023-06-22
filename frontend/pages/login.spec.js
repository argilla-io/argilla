import { shallowMount } from "@vue/test-utils";
import Login from "./login.vue";

const stubs = ["BaseLoading", "brand-logo", "geometric-shape-a", "base-button"];

describe("Login page should", () => {
  it("still in the same page if the auth token is not valid", () => {
    const userLoginSpy = jest.spyOn(Login.methods, "userLogin");

    shallowMount(Login, {
      mocks: {
        $route: {
          query: {
            auth: "INVALID",
          },
        },
      },
    });

    expect(userLoginSpy).toHaveBeenCalledTimes(0);
  });

  it("still in the same page if the auth token query params is empty", () => {
    const userLoginSpy = jest.spyOn(Login.methods, "userLogin");

    shallowMount(Login, {
      mocks: {
        $route: {
          query: {},
        },
      },
    });

    expect(userLoginSpy).toHaveBeenCalledTimes(0);
  });

  it("try to login user when the auth token is valid", () => {
    const userLoginSpy = jest.spyOn(Login.methods, "userLogin");

    shallowMount(Login, {
      stubs,
      mocks: {
        $route: {
          query: {
            auth: "eyJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiIxMjM0NTY3OCJ9",
          },
        },
      },
    });

    expect(userLoginSpy).toHaveBeenCalledTimes(1);
  });

  it("the auth token is valid when the object has the username and password", () => {
    const auth = btoa(
      JSON.stringify({ username: "USERNAME", password: "PASSWORD" })
    );

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

    expect(wrapper.vm.authToken).toEqual({
      username: "USERNAME",
      password: "PASSWORD",
    });
    expect(wrapper.vm.hasAuthToken).toBeTruthy();
  });

  it("the auth token is not valid when the object has username but no password", () => {
    const auth = btoa(JSON.stringify({ username: "USERNAME", password: "" }));

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

    expect(wrapper.vm.authToken).toBeUndefined();
    expect(wrapper.vm.hasAuthToken).toBeFalsy();
  });

  it("the auth token is not valid when the object has no username but password", () => {
    const auth = btoa(JSON.stringify({ username: "", password: "PASSWORD" }));

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

    expect(wrapper.vm.authToken).toBeUndefined();
    expect(wrapper.vm.hasAuthToken).toBeFalsy();
  });

  it("the auth token is not valid when the object has no username and no password", () => {
    const auth = btoa(JSON.stringify({ username: "", password: "" }));

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

    expect(wrapper.vm.authToken).toBeUndefined();
    expect(wrapper.vm.hasAuthToken).toBeFalsy();
  });

  it("the auth token is not valid when the object other object structure", () => {
    const auth = btoa(JSON.stringify({ foo: "bar" }));

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

    expect(wrapper.vm.authToken).toBeUndefined();
    expect(wrapper.vm.hasAuthToken).toBeFalsy();
  });

  it("show the loading logo when the token is valid", () => {
    const auth = btoa(
      JSON.stringify({ username: "USERNAME", password: "PASSWORD" })
    );

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
