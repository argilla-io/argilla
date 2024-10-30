import { useUser } from "~/v1/infrastructure/services/useUser";
import { useRunningEnvironment } from "~/v1/infrastructure/services/useRunningEnvironment";
export const useImportFromPython = () => {
  const { isRunningOnHuggingFace } = useRunningEnvironment();
  const { getUser } = useUser();

  const user = getUser();

  const isRunningOnHF = isRunningOnHuggingFace();

  const snippet = `
# pip install argilla
# to run this code snippet

import argilla as rg

client = rg.Argilla(
    api_url="${window.location.origin}",
    api_key="${user.apiKey}",
)

settings = rg.Settings(
    guidelines="These are some guidelines.",
    fields=[
        rg.TextField(
            name="text",
        ),
    ],
    questions=[
        rg.LabelQuestion(
            name="label",
            labels=["yes", "no"]
        ),
    ],
)

dataset = rg.Dataset(
    name="my_dataset",
    settings=settings,
)

dataset.create()

records = [
    {
        "text": "Do you need oxygen to breathe?",
        "label": "yes",
    }
]

dataset.records.log(records)
`;

  return { snippet, isRunningOnHF };
};
