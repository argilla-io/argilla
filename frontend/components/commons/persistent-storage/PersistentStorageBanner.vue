<template>
  <BaseBanner
    :message="
      isAdminOrOwnerRole
        ? $t('persistentStorage.adminOrOwner')
        : $t('persistentStorage.annotator')
    "
    :button-text="$t('learnMore')"
    :button-link="$config.documentationPersistentStorage"
    type="warning"
    on-dismiss="onDismiss"
  />
</template>

<script>
import { usePersistentStorageViewModel } from "./usePersistentStorageViewModel";
export default {
  data() {
    return {
      showBanner: false,
    };
  },
  methods: {
    onDismiss() {
      console.log("hide banner");
    },
  },
  setup() {
    return usePersistentStorageViewModel();
  },
  async fetch() {
    this.showBanner = await this.hasPersistentStorageWarning();
  },
};
</script>
