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
        :color="selectedEntity.color"
        :text="selectedEntity.name"
        @on-clear="removeSelectedOption(selectedEntity)"
      ></EntityBadge>
      <input
        ref="search"
        class="span-entity__input"
        type="text"
        autocomplete="off"
        autofocus
        v-model="searchText"
        @keydown.arrow-up.stop=""
        @keydown.arrow-down.stop=""
        @keydown.arrow-right.stop=""
        @keydown.arrow-left.stop=""
        @keydown.delete.exact.stop=""
        @keydown.enter.exact.stop=""
        @keydown.backspace.exact.stop=""
      />
    </div>
    <ul class="span-entity__dropdown__content">
      <li>
        <BaseButton
          v-for="(entity, index) in filteredEntities"
          :key="entity.id"
          class="span-entity__dropdown__item"
          :class="{ '--preselected': preSelectionIndex === index }"
          @click="selectEntity(entity)"
          @mouseover.native="preSelectionIndex = index"
        >
          <EntityBadge
            class="span-entity__badge"
            :color="entity.color"
            :text="entity.name"
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
    selectedEntity: {
      type: Object,
      required: true,
    },
    entities: {
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
    filteredEntities() {
      return this.availableEntities.filter((entity) =>
        entity.name.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
    availableEntities() {
      return this.entities.filter(
        (entity) => entity.id !== this.selectedEntity.id
      );
    },
    optionsLength() {
      return this.filteredEntities.length;
    },
  },
  methods: {
    selectEntity(entity) {
      this.$emit("on-replace-entity", entity);
    },
    removeSelectedOption() {
      this.$emit("on-remove-entity");
    },
    includePreselectedOption() {
      if (!this.filteredEntities.length) return;
      this.selectEntity(this.filteredEntities[this.preSelectionIndex]);
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
    this.$nextTick(() => {
      this.$refs.search?.focus();
    });
    this.preselectedEntity = this.filteredEntities[0];
  },
};
</script>

<style lang="scss" scoped>
@import url("https://fonts.googleapis.com/css2?family=Roboto+Condensed&display=swap");
.span-entity {
  &__dropdown {
    position: relative;
    display: flex;
    flex-direction: column;
    border-radius: $border-radius;
    background-color: palette(white);
    box-shadow: $shadow;
    z-index: 100;
    &__header {
      display: flex;
      gap: $base-space;
      background: $black-4;
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
        background-color: $black-4;
      }
    }
  }
  &__badge.badge {
    @include font-size(12px);
  }
  &__input {
    height: $base-space * 2;
    width: 100px;
    background: transparent;
    border: none;
    @include font-size(12px);
    &:focus-visible {
      outline: 0;
    }
    @include input-placeholder {
      color: $black-37;
    }
  }
}
</style>
