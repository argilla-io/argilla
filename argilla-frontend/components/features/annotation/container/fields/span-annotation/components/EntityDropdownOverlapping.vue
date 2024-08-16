<template>
  <div
    class="span-entity__dropdown"
    @keyup.enter="includePreselectedOption"
    @keyup.up="preselectPreviousOption"
    @keyup.down="preselectNextOption"
    v-click-outside="selectOptions"
  >
    <div class="span-entity__dropdown__header">
      <div class="span-entity__badges">
        <EntityBadge
          v-for="entity in selection"
          :key="entity.id"
          class="span-entity__badge--active"
          :color="entity.color"
          :text="entity.text"
          @on-clear="excludeOption(entity)"
          >{{ entity }}</EntityBadge
        >
      </div>
      <BaseButton
        v-if="selection.length"
        class="span-entity__badges__close-button"
        @click="excludeAll"
        title="Clear all"
      >
        <svgicon
          class="span-entity__badges__close-button__icon"
          name="close"
          width="10"
          height="10"
      /></BaseButton>
      <input
        ref="search"
        class="span-entity__input"
        type="text"
        autocomplete="off"
        :placeholder="selection.length ? '' : $nuxt.$t('search')"
        autofocus
        v-model="searchText"
        @keydown.stop=""
      />
    </div>
    <ul class="span-entity__dropdown__content">
      <li>
        <BaseCheckbox
          v-for="(option, index) in filteredOptions"
          :key="option.id"
          class="span-entity__dropdown__item"
          :class="{ '--preselected': preSelectionIndex === index }"
          :value="option"
          v-model="selection"
          @mouseover.native="preSelectionIndex = index"
        >
          <EntityBadge
            class="span-entity__badge"
            :color="option.color"
            :text="option.text"
          ></EntityBadge>
        </BaseCheckbox>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "EntityComponent",
  props: {
    options: {
      type: Array,
      required: true,
    },
    spanInRange: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      searchText: "",
      preSelectionIndex: 0,
      selection: [],
    };
  },
  computed: {
    filteredOptions() {
      return this.options.filter((entity) =>
        entity.text.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
    optionsLength() {
      return this.filteredOptions.length;
    },
  },
  methods: {
    selectOptions() {
      const removedSpans = this.spanInRange.filter(
        ({ entity }) =>
          !this.selection.map((entity) => entity.id).includes(entity.id)
      );

      removedSpans.forEach((span) => {
        this.$emit("on-remove-span", span);
      });

      const addedSpans = this.selection.filter(
        (entity) =>
          !this.spanInRange.some((span) => span.entity.id === entity.id)
      );

      addedSpans.forEach((entity) => {
        this.$emit("on-add-span-base-on", this.spanInRange[0], entity);
      });
    },
    excludeOption(entityOpt) {
      this.selection = this.selection.filter(
        (entity) => entity.id !== entityOpt.id
      );
    },
    excludeAll() {
      this.selection = [];
    },
    includeOption(option) {
      this.selection.push(option);
    },
    includePreselectedOption() {
      const option = this.filteredOptions[this.preSelectionIndex];
      if (!this.filteredOptions.length) return;
      if (this.selection.includes(option)) {
        this.excludeOption(option);
      } else {
        this.includeOption(option);
      }
      this.preSelectionIndex = 0;
    },
    preselectNextOption() {
      this.preSelectionIndex === this.optionsLength - 1
        ? (this.preSelectionIndex = 0)
        : this.preSelectionIndex++;
    },
    preselectPreviousOption() {
      this.preSelectionIndex === 0
        ? (this.preSelectionIndex = this.optionsLength - 1)
        : this.preSelectionIndex--;
    },
  },
  watch: {
    searchText() {
      this.preSelectionIndex = 0;
    },
    selection() {
      this.$nextTick(() => {
        this.$refs.search.focus();
      });
    },
  },
  mounted() {
    this.preselectedEntity = this.filteredOptions[0];
    this.selection = this.spanInRange.map(({ entity }) => {
      return this.options.find((option) => option.id === entity.id);
    });
    this.$refs.search.focus();
  },
};
</script>

<style lang="scss" scoped>
@import url("https://fonts.googleapis.com/css2?family=Roboto+Condensed&display=swap");
.span-entity {
  &__dropdown {
    position: fixed;
    display: flex;
    flex-direction: column;
    border-radius: $border-radius;
    background-color: var(--bg-accent-grey-2);
    box-shadow: $shadow;
    z-index: 100;
    &__header {
      display: flex;
      flex-direction: column;
      gap: $base-space;
      background: var(--bg-opacity-4);
      padding: calc($base-space / 2);
    }
    &__content {
      padding: calc($base-space / 2);
      margin: 0;
      list-style: none;
      overflow: auto;
      max-height: 200px;
    }
    &__item {
      display: flex;
      width: 100%;
      justify-content: space-between;
      padding: calc($base-space / 2);
      border-radius: 4px;
      :deep(.checkbox__container) {
        background: none !important;
        border: 0 !important;
        width: auto !important;
      }
      :deep(label) {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      &.checkbox :deep(.checkbox__container .svg-icon) {
        display: inline-block;
        fill: var(--bg-opacity-37);
        min-width: 16px;
        min-height: 16px;
      }
      &.--preselected {
        background-color: var(--bg-opacity-4);
      }
    }
  }
  &__badges {
    display: flex;
    gap: calc($base-space / 2);
    flex-wrap: wrap;
    max-width: 142px;
    &__close-button {
      position: absolute;
      top: calc($base-space / 2);
      right: calc($base-space / 2);
      padding: calc($base-space / 2);
      background: var(--bg-opacity-37);
      border-radius: $border-radius-rounded;
      &:hover {
        background: var(--bg-opacity-54);
      }
      &__icon {
        color: var(--bg-accent-grey-1);
      }
    }
  }
  &__badge.badge {
    @include font-size(12px);
    cursor: pointer;
  }
  &__input {
    height: $base-space * 2;
    width: 160px;
    background: transparent;
    border: none;
    color: var(--fg-primary);
    @include font-size(12px);
    &:focus-visible {
      outline: 0;
    }
    @include input-placeholder {
      color: var(--fg-tertiary);
    }
  }
}
</style>
