<template>
  <div class="datasets-filter" v-if="workspaces.length">
    <BaseDropdown :visible="visibleDropdown" @visibility="onToggleVisibility">
      <span slot="dropdown-header"
        ><WorkspacesFilterButton
          :is-active="visibleDropdown || !!selectedWorkspaces.length"
      /></span>
      <span slot="dropdown-content" class="datasets-filter__container">
        <div class="datasets-filter__content">
          <WorkspaceSelector
            :workspaces="workspaces"
            :selected-workspaces="selectedWorkspaces"
          />
        </div>
      </span>
    </BaseDropdown>
  </div>
</template>

<script>
import "assets/icons/chevron-left";

export default {
  props: {
    workspaces: {
      type: Array,
      required: true,
    },
    selectedWorkspaces: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "selectedWorkspaces",
    event: "on-change-workspaces-filter",
  },
  data() {
    return {
      visibleDropdown: false,
    };
  },
  watch: {
    selectedWorkspaces() {
      this.$emit("on-change-workspaces-filter", this.selectedWorkspaces);
    },
  },
  methods: {
    onToggleVisibility(value) {
      this.visibleDropdown = value;
    },
  },
};
</script>
<style lang="scss" scoped>
$datasets-filter-width: 300px;
.datasets-filter {
  &__container {
    display: block;
    width: $datasets-filter-width;
  }
  &__header {
    display: flex;
    gap: $base-space;
    align-items: center;
    justify-content: space-between;
    padding: $base-space $base-space * 2;
    cursor: pointer;
    &:hover {
      background: var(--bg-opacity-4);
    }
  }
  &__content {
    padding: $base-space;
  }
  &__categories {
    padding: $base-space;
    background: var(--bg-accent-grey-2);
    border-radius: $border-radius;
  }
  &__button.button {
    padding: 10px;
  }
  :deep(.dropdown__header:hover) {
    background: none;
  }
  :deep(.dropdown__content) {
    right: 0;
    left: auto;
  }
}
</style>
