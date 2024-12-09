import { ref, watch } from "vue";
import { useUser } from "~/v1/infrastructure/services";
import { useClipboard } from "~/v1/infrastructure/services/useClipboard";
import { useDataset } from "~/v1/infrastructure/storage/DatasetStorage";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";
import { useTeamProgress } from "~/v1/infrastructure/storage/TeamProgressStorage";

export const useShareViewModel = () => {
  const { copy } = useClipboard();
  const { user } = useUser();
  const { state: metrics } = useMetrics();
  const { state: dataset } = useDataset();
  const { state: progress } = useTeamProgress();

  const isDialogOpen = ref(false);
  const imageLink = ref("");

  const copyOnClipboard = () => {
    closeDialog();

    const url = new URL(`${window.location.origin}/share-your-progress`);
    const params = new URLSearchParams("");
    params.set("user_name", user.value.userName);
    params.set("records_submitted", metrics.submitted.toString());
    params.set("team_progress", progress.percentage.completed.toString());
    params.set("dataset_name", dataset.name);
    params.set("dataset_id", dataset.id);

    url.search = params.toString();

    const textToCopy = `I've just contributed ${
      metrics.submitted
    } examples to this dataset:

${url.toString()}`;

    copy(textToCopy);
  };

  const createImageLink = () => {
    const url = new URL("https://argilla.imglab-cdn.net/dibt/dibt_v2.png");
    const params = new URLSearchParams(url.search);
    params.set("width", "1200");
    params.set("text-width", "700");
    params.set("text-height", "590");
    params.set("text-padding", "60");
    params.set("text-color", "39,71,111");
    params.set("text-x", "460");
    params.set("text-y", "40");
    params.set("format", "png");
    params.set("dpr", "2");

    params.set(
      "text",
      `<span>
<span size="9pt" weight="bold">@${user.value.userName}</span>
I've just contributed <span weight="bold">${metrics.submitted}</span> examples to this dataset:
<span size="9pt" weight="bold">${dataset.name}</span></span>

<span size="8pt">Team progress</span>
<span weight="bold">${progress.percentage.completed}%</span>`
    );

    return `${url.origin}${url.pathname}?${params.toString()}`;
  };

  const openDialog = () => {
    imageLink.value = createImageLink();

    isDialogOpen.value = true;
  };

  const closeDialog = () => {
    isDialogOpen.value = false;
  };

  watch(
    () => metrics.submitted,
    () => {
      fetch(createImageLink());
    }
  );

  return {
    imageLink,
    isDialogOpen,
    openDialog,
    closeDialog,
    copyOnClipboard,
  };
};
