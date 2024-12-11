<template>
  <div
    class="span-entity__dropdown"
    @keyup.enter="includePreselectedOption"
    @keyup.up="preselectPreviousOption"
    @keyup.down="preselectNextOption"
  >
    <div class="span-entity__dropdown__header">
      <EntityBadge
        class="span-entity__badge--active"
        :color="selectedOption.color"
        :text="selectedOption.text"
      ></EntityBadge>
      <input
        ref="search"
        class="span-entity__input"
        type="text"
        autocomplete="off"
        placeholder=""
        autofocus
        v-model="searchText"
        @keydown.stop=""
      />
    </div>
    <ul class="span-entity__dropdown__content">
      <li>
        <BaseButton
          v-for="(option, index) in filteredOptions"
          :key="option.id"
          class="span-entity__dropdown__item"
          :class="{ '--preselected': preSelectionIndex === index }"
          @click="selectOption(option)"
          @mouseover.native="preSelectionIndex = index"
        >
          <EntityBadge
            class="span-entity__badge"
            :color="option.color"
            :text="option.text"
          ></EntityBadge>
        </BaseButton>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "EntityComponent",
  props: {
    selectedOption: {
      type: Object,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      searchText: "",
      preSelectionIndex: 0,
    };
  },
  computed: {
    filteredOptions() {
      return this.availableOptions.filter((entity) =>
        entity.text.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
    availableOptions() {
      return this.options.filter(
        (entity) => entity.id !== this.selectedOption.id
      );
    },
    optionsLength() {
      return this.filteredOptions.length;
    },
  },
  methods: {
    selectOption(option) {
      this.$emit("on-replace-entity", option);
    },
    includePreselectedOption() {
      if (!this.filteredOptions.length) return;
      this.selectOption(this.filteredOptions[this.preSelectionIndex]);
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
  },
  mounted() {
    this.preselectedEntity = this.filteredOptions[0];
    this.$refs.search.focus();
  },
};
</script>

<style lang="scss" scoped>
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
    &__item.button {
      display: flex;
      width: 100%;
      padding: calc($base-space / 2);
      border-radius: 4px;
      &.--preselected {
        background-color: var(--bg-opacity-4);
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
