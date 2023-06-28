import { defineStore } from "pinia";
import { create } from "./non-reactive";

interface Class<T> extends Function {
  new (...args: any[]): T;
}

export const useStoreFor = <T>(ctor: Class<T>) => {
  return defineStore(ctor.name, {
    state: () => ({
      state: new ctor() as T,
    }),
    actions: {
      save(state: T) {
        this.$patch({ state });
      },
      get(): T {
        return create(ctor, this.$state.state);
      },
    },
  });
};
