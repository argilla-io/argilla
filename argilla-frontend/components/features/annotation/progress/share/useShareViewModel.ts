import { ref } from "vue";
import {
  useNotifications,
  useTranslate,
  useUser,
} from "~/v1/infrastructure/services";
import { useClipboard } from "~/v1/infrastructure/services/useClipboard";
import { useDataset } from "~/v1/infrastructure/storage/DatasetStorage";
import { useMetrics } from "~/v1/infrastructure/storage/MetricsStorage";
import { useTeamProgress } from "~/v1/infrastructure/storage/TeamProgressStorage";

export const useShareViewModel = () => {
  const { t } = useTranslate();
  const { copy } = useClipboard();
  const { user } = useUser();
  const { state: metrics } = useMetrics();
  const { state: dataset } = useDataset();
  const notification = useNotifications();
  const { state: progress } = useTeamProgress();

  const isDialogOpen = ref(false);
  const imageLink = ref("");

  const copyOnClipboard = () => {
    closeDialog();

    copy(imageLink.value);

    notification.notify({
      message: t("copiedToClipboard"),
      type: "success",
    });
  };

  const createImageLink = () => {
    const url = new URL("https://argilla.imglab-cdn.net/dibt/dibt.png");
    const params = new URLSearchParams(url.search);
    params.set("width", "900");
    params.set("text-width", "450");
    params.set("text-height", "750");
    params.set("text-weight", "bold");
    params.set("text-padding", "60");
    params.set("text-color", "39,71,111");
    params.set("format", "png");
    params.set("dpr", "2");

    params.set(
      "text",
      `<span size="10pt">@${user.value.userName}</span>

I've just submitted ${metrics.submitted} rows reviews for:

<span size="10pt">${dataset.name}</span>

<span size="8pt" weight="normal">Team progress</span>
${progress.percentage.completed}%`
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

  return {
    imageLink,
    isDialogOpen,
    openDialog,
    closeDialog,
    copyOnClipboard,
  };
};
