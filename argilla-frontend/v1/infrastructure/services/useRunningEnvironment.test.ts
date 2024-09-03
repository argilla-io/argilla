import Container, { register } from "ts-injecty";
import { useRunningEnvironment } from "./useRunningEnvironment";
import { GetEnvironmentUseCase } from "~/v1/domain/usecases/get-environment-use-case";
import { Environment } from "~/v1/domain/entities/environment/Environment";

const loadMockedURL = (url: string) => {
  Object.defineProperty(window, "location", {
    value: {
      href: url,
    },
    writable: true,
  });
};

describe("useRunningEnvironment", () => {
  describe("isRunningOnHuggingFace", () => {
    test("should return true and user name if argilla is running on huggingface", () => {
      loadMockedURL("https://huggingface.co/spaces/damianpumar/awesome-space");

      const { isRunningOnHuggingFace } = useRunningEnvironment();

      expect(isRunningOnHuggingFace()).toBeTruthy();
    });

    test("should be false if argilla is not running on huggingface", () => {
      loadMockedURL("https://other.domain.com/damianpumar/awesome-space");

      const { isRunningOnHuggingFace } = useRunningEnvironment();

      expect(isRunningOnHuggingFace()).toBeFalsy();
    });
  });

  describe("getHuggingFaceSpace", () => {
    test("should return the space name if argilla is running on huggingface", async () => {
      const mockedGetEnvironmentUseCase = () => ({
        getEnvironment: () =>
          Promise.resolve(
            new Environment(
              {
                showHuggingfaceSpacePersistentStorageWarning: false,
              },
              {
                spaceAuthorName: "USER_NAME_FAKE",
                spaceRepoName: "AWESOME_SPACE",
                spaceHost: "huggingface.co",
                spaceId: "USER_NAME_FAKE/AWESOME_SPACE",
                spacePersistentStorageEnabled: true,
                spaceSubdomain: "spaces",
                spaceTitle: "AWESOME_SPACE",
              }
            )
          ),
      });

      Container.register([
        register(GetEnvironmentUseCase)
          .withDependency(mockedGetEnvironmentUseCase)
          .build(),
      ]);

      const { getHuggingFaceSpace } = useRunningEnvironment();
      const space = await getHuggingFaceSpace();

      expect(space).toEqual({
        user: "USER_NAME_FAKE",
        space: "AWESOME_SPACE",
        host: "huggingface.co",
      });
    });
  });
});
