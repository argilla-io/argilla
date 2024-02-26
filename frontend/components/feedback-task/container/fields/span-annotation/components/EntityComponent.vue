<template>
  <div :style="{ left: entityPosition.left, top: entityPosition.top }">
    <div @click="toggleDropdown()" class="span-entity" v-if="!visibleDropdown">
      {{ selectedEntity.text }}
    </div>
    <div v-else class="span-entity__dropdown" v-click-outside="hideDropdown">
      <div class="span-entity__dropdown__header">
        <EntityBadge
          class="span-entity__badge--active"
          :color="selectedEntityColor"
          :text="selectedEntity.text"
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
        <li
          class="span-entity__dropdown__item"
          v-for="entity in filteredEntities"
          :key="entity.id"
          @click="selectEntity(entity)"
        >
          <EntityBadge
            class="span-entity__badge"
            :color="entity.color"
            :text="entity.name"
          ></EntityBadge>
        </li>
      </ul>
    </div>
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
    spanQuestion: {
      type: Object,
    },
    entityPosition: {
      left: {
        type: String,
        required: true,
      },
      top: {
        type: String,
        required: true,
      },
    },
  },
  data() {
    return {
      visibleDropdown: false,
      searchText: "",
    };
  },
  computed: {
    selectedEntityColor() {
      return this.entities.find((e) => e.id === this.selectedEntity.id).color;
    },
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
    entities() {
      return this.spanQuestion.answer.entities;
    },
  },
  methods: {
    selectEntity(entity) {
      this.selectEntityGlobally(entity);
      this.hideDropdown();
    },
    selectEntityGlobally(entity) {
      this.entities.find((e) => e.isSelected).isSelected = false;
      this.entities.find((e) => e.id === entity.id).isSelected = true;
    },
    removeSelectedOption(entity) {
      console.log("remove entity", entity);
      this.hideDropdown();
    },
    toggleDropdown() {
      this.visibleDropdown = !this.visibleDropdown;
    },
    hideDropdown() {
      this.visibleDropdown = false;
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.$refs.search && this.$refs.search.focus();
    });
  },
};
</script>

<style lang="scss" scoped>
@import url("https://fonts.googleapis.com/css2?family=Roboto+Condensed&display=swap");
.span-entity {
  text-transform: uppercase;
  font-family: "Roboto Condensed", sans-serif;
  margin-left: 2px;
  cursor: pointer;
  &__dropdown {
    position: relative;
    display: flex;
    flex-direction: column;
    border-radius: $border-radius;
    background-color: palette(white);
    box-shadow: $shadow;
    z-index: 100;
    margin-top: 5px;
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
    &__item {
      display: flex;
      padding: calc($base-space / 4);
      border-radius: 4px;
      cursor: pointer;
      &:hover {
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
.highlight__entity {
  display: block;
  margin-top: 14px;
  font-size: 10px;
  position: absolute;
}
</style>

