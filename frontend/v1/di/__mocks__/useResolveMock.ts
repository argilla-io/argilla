import Container, { register } from "ts-injecty";
import { Class } from "ts-injecty/types";

export const useResolveMock = <T>(ctor: Class<T>, mocked: Object) => {
  Container.register([register(ctor.name).withImplementation(mocked).build()]);
};
