<template>
  <div :style="{ left: entityPosition.left, top: entityPosition.top }">
    <div @click="toggleDropdown()" class="span-entity" v-if="!visibleDropdown">
      {{ selectedEntity.name }}
    </div>
    <div v-else class="span-entity__dropdown" v-click-outside="hideDropdown">
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
    entity: {
      type: Object,
      required: true,
    },
    spanQuestion: {
      type: Object,
    },
    entityPosition: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      visibleDropdown: false,
      searchText: "",
    };
  },
  computed: {
    selectedEntity() {
      return this.entities.find((e) => e.id === this.entity.id);
    },
    filteredEntities() {
      return this.availableEntities.filter((entity) =>
        entity.name.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
    availableEntities() {
      return this.entities.filter((entity) => entity.id !== this.entity.id);
    },
    entities() {
      return this.spanQuestion.answer.entities;
    },
  },
  methods: {
    selectEntity(entity) {
      this.$emit("on-replace-entity", entity);
      this.hideDropdown();
    },
    removeSelectedOption() {
      this.$emit("on-remove-entity");
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
      this.$refs.search?.focus();
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
  margin-top: 15px;
  font-size: 10px;
  position: absolute;
}
</style>
