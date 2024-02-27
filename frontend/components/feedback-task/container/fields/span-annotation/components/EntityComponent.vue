<template>
  <div :style="{ left: entityPosition.left, top: entityPosition.top }">
    <div @click="toggleDropdown()" class="span-entity" v-if="!visibleDropdown">
      {{ selectedEntity.name }}
    </div>
    <EntityComponentDropdown
      v-if="visibleDropdown"
      :selectedEntity="selectedEntity"
      :entities="entities"
      @on-replace-entity="selectEntity"
      @on-remove-entity="removeSelectedOption"
      v-click-outside="hideDropdown"
    />
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
    };
  },
  computed: {
    selectedEntity() {
      return this.entities.find((e) => e.id === this.entity.id);
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
};
</script>

<style lang="scss" scoped>
@import url("https://fonts.googleapis.com/css2?family=Roboto+Condensed&display=swap");
.span-entity {
  text-transform: uppercase;
  font-family: "Roboto Condensed", sans-serif;
  margin-left: 2px;
  cursor: pointer;
}
.highlight__entity {
  display: block;
  margin-top: 15px;
  font-size: 10px;
  position: absolute;
}
</style>
