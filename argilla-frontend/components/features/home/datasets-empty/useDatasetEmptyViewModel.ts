import { useRunningEnvironment } from "~/v1/infrastructure/services/useRunningEnvironment";
import { useUser } from "~/v1/infrastructure/services/useUser";

const HF_PREFIX = "[hf_]";
const LOCAL_PREFIX = "[local_]";
const HF_HOST = "[HF_HOST]";
const USER_API_KEY = "[USER_API_KEY]";
const LOCAL_HOST = "[LOCAL_HOST]";

export const useDatasetEmptyViewModel = () => {
  const { isRunningOnHuggingFace, getHuggingFaceSpace } =
    useRunningEnvironment();
  const { getUser } = useUser();

  const replaceLocalData = (rows) => {
    const content = [];
    const user = getUser();

    for (const row of rows) {
      if (row.includes(HF_PREFIX)) continue;

      if (row.includes(LOCAL_PREFIX)) {
        content.push(
          row
            .replace(LOCAL_PREFIX, "")
            .replace(LOCAL_HOST, window.location.origin)
        );
        continue;
      }

      if (row.includes(USER_API_KEY)) {
        content.push(row.replace(USER_API_KEY, user.apiKey));
        continue;
      }

      content.push(row);
    }

    return Promise.resolve(content.join("\n"));
  };

  const replaceHFData = async (rows) => {
    const user = getUser();
    const hfEnvironment = await getHuggingFaceSpace();

    const content = [];

    for (const row of rows) {
      if (row.includes(LOCAL_PREFIX)) continue;

      if (row.includes(HF_PREFIX)) {
        content.push(
          row.replace(HF_PREFIX, "").replace(HF_HOST, hfEnvironment.host)
        );

        continue;
      }

      if (row.includes(USER_API_KEY)) {
        content.push(row.replace(USER_API_KEY, user.apiKey));
        continue;
      }

      content.push(row);
    }

    return content.join("\n");
  };

  const preFillData = (startPage) => {
    const rows = startPage.body.split("\n");

    if (isRunningOnHuggingFace()) return replaceHFData(rows);

    return replaceLocalData(rows);
  };

  return {
    preFillData,
  };
};
