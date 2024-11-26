<template>
  <BaseBadgeSkeleton font-size="11px" v-if="isFieldsLoading" :quantity="2" />
  <div class="fields" v-else>
    <span class="fields__title">{{ $t("fields") }}</span>
    <div class="fields__badges">
      <BaseBadge
        v-for="field in fields"
        :key="field.id"
        :text="$t(field.type)"
        font-size="10px"
      />
    </div>
  </div>
</template>
<script>
import { useDatasetFields } from "./useDatasetFields";

export default {
  name: "DatasetFields",
  props: {
    dataset: {
      type: Object,
    },
  },
  setup(props) {
    return useDatasetFields(props);
  },
};
</script>

<style scoped lang="scss">
.fields {
  display: flex;
  flex-wrap: wrap;
  gap: calc($base-space / 2);
  &__title {
    @include font-size(12px);
    color: var(--fg-secondary);
    min-width: $base-space * 7;
  }
  &__badges {
    display: flex;
    flex-wrap: wrap;
    gap: calc($base-space / 2);
  }
}
</style>
