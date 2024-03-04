<template>
  <div
    class="span-entity__wrapper"
    :style="{ left: entityPosition.left, top: entityPosition.top }"
  >
    <div @click="toggleDropdown()" class="span-entity" v-if="!visibleDropdown">
      {{ selectedOption.text }}
    </div>
    <EntityComponentDropdown
      v-if="visibleDropdown"
      :selectedOption="selectedOption"
      :options="options"
      @on-replace-option="selectOption"
      @on-remove-option="removeSelectedOption"
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
    selectedOption() {
      return this.options.find((e) => e.id === this.entity.id);
    },
    options() {
      return this.spanQuestion.answer.options;
    },
  },
  methods: {
    selectOption(option) {
      this.$emit("on-replace-option", option);
      this.hideDropdown();
    },
    removeSelectedOption() {
      this.$emit("on-remove-option");
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
  margin-top: -1px;
  max-width: v-bind("entityPosition.width");
  min-width: 10px;
  background: palette(grey, 800);
  text-transform: uppercase;
  font-family: "Roboto Condensed", sans-serif;
  cursor: pointer;
  @include truncate;
  transition: background 0.3s;
  &__wrapper {
    position: absolute;
    display: block;
    margin-top: 20px;
    line-height: 1;
    @include font-size(11px);
  }
  &:hover {
    position: relative;
    max-width: none;
    z-index: 1;
    background: v-bind("selectedOption.color");
    transition: background 0.3s;
  }
}
</style>
