<template>
  <BaseBanner
    v-if="showBanner"
    :message="
      isAdminOrOwnerRole
        ? $t('persistentStorage.adminOrOwner')
        : $t('persistentStorage.annotator')
    "
    :button-text="$t('learnMore')"
    :button-link="$config.documentationPersistentStorage"
    type="warning"
  />
</template>

<script>
import { usePersistentStorageViewModel } from "./usePersistentStorageViewModel";

export default {
  setup() {
    return usePersistentStorageViewModel();
  },
};
</script>
