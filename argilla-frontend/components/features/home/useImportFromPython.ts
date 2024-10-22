import { useUser } from "~/v1/infrastructure/services/useUser";
import { useRunningEnvironment } from "~/v1/infrastructure/services/useRunningEnvironment";
export const useImportFromPython = () => {
  const { isRunningOnHuggingFace } = useRunningEnvironment();
  const { getUser } = useUser();

  const user = getUser();

  const HFHeader = isRunningOnHuggingFace()
    ? `headers={"Authorization": f"Bearer {HF_TOKEN}"}`
    : "";

  const snippet = `
import argilla as rg

client = rg.Argilla(
    api_url="${window.location.origin}",
    api_key="${user.apiKey}",
    ${HFHeader}
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
            labels=["label_1", "label_2"]
        ),
    ],
)

dataset = rg.Dataset(
    name="my_dataset",
    workspace="my_workspace",
    settings=settings,
)

records = [
    {
        "text": "Do you need oxygen to breathe?",
        "label": "label_1",
    }
]

dataset.records.log(records)
`;

  return { snippet };
};
