import { defineStore } from "pinia";
import { create } from "./non-reactive";

interface Class<T> extends Function {
  new (...args: any[]): T;
}

export interface ImplicitStorage<T> {
  save(state: T);
  get(): T;
}

type State<T> = {
  state: T;
};

type Store<T, S> = () => State<T> & S & ImplicitStorage<T>;

export const useStoreFor = <T, S>(Ctor: Class<T>) => {
  const store = defineStore(Ctor.name, {
    state: () => ({
      state: new Ctor() as T,
    }),
    actions: {
      save(state: T) {
        this.$patch({ state });
      },
      get(): T {
        return create(Ctor, this.state);
      },
    },
  });

  return store as Store<T, S>;
};
