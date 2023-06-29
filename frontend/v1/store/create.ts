import { defineStore } from "pinia";
import { create } from "./non-reactive";

interface Class<T> extends Function {
  new (...args: any[]): T;
}

export const useStoreFor = <T, R>(Ctor: Class<T>) => {
  const store = defineStore(Ctor.name, {
    state: () => ({
      state: new Ctor() as T,
    }),
    actions: {
      save(state: T) {
        this.$patch({ state });
      },
      get(): T {
        return create(Ctor, this.$state.state);
      },
    },
  });

  return store as R & typeof store;
};
