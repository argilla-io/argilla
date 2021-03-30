<template>
  <div
    :class="[
      'entities__container',
      activeEntity ? 'entities__container--multiple' : '',
    ]"
  >
    <span
      v-for="(entity, index) in filteredEntities.slice(0, entitiesNumber)"
      :key="index"
      class="entity"
      :class="[
        'color_' + entities.indexOf(entity),
        activeEntity === entity.text ? 'active' : '',
        annotationMode ? 'non-selectable--show-sort-code' : 'non-selectable',
      ]"
      @click="onActiveEntity(entity)"
    >
      {{ entity.text }}
      <span class="entity__sort-code">[{{ entity.shortCut }}]</span>
    </span>
    <ReButton
      v-if="filteredEntities.length >= entitiesNumber"
      class="entities__container__button"
      @click="toggleEntitiesNumber"
      >{{
        entitiesNumber === filteredEntities.length ? "Show less" : "Show all"
      }}</ReButton
    >
    <p
      v-if="!addnewSlotVisible && annotationMode"
      class="entity__new"
      @click="openAddSlot()"
    >
      + New Entity
    </p>
    <div v-if="addnewSlotVisible" class="entity__new__container">
      <input
        ref="addSlotInput"
        v-model="newSlot"
        class="entity__new__input"
        type="text"
        placeholder="New entity"
        @keyup.enter="addEntity(newSlot)"
      />
      <svgicon name="cross" @click="addnewSlotVisible = false" />
    </div>
  </div>
</template>

<script>
import "assets/icons/check";
import "assets/icons/cross";

export default {
  props: {
    entities: {
      type: Array,
      required: true,
    },
    dataset: {
      type: Object,
      required: true,
    },
    annotationMode: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    activeEntity: undefined,
    searchEntity: "",
    newSlot: "",
    showEntitySelector: false,
    addnewSlotVisible: false,
    entitiesNumber: 12,
  }),
  computed: {
    filteredEntities() {
      return this.entities.filter((entity) =>
        entity.text.toLowerCase().includes(this.searchEntity.toLowerCase())
      );
    },
    entityKey() {
      return Object.keys(this.entities);
    },
  },
  methods: {
    toggleEntitiesNumber() {
      if (this.entitiesNumber === this.filteredEntities.length) {
        this.entitiesNumber = 12;
      } else {
        this.entitiesNumber = this.filteredEntities.length;
      }
    },
    onActiveEntity(entity) {
      if (this.annotationMode) {
        if (this.activeEntity === entity.text) {
          this.activeEntity = undefined;
        } else {
          this.activeEntity = entity.text;
        }
      }
    },
    openAddSlot() {
      this.addnewSlotVisible = true;
      this.$nextTick(() => this.$refs.addSlotInput.focus());
    },
    async addEntity(entity) {
      this.addnewSlotVisible = false;
      this.dataset.$dispatch("setEntities", {
        dataset: this.dataset,
        entities: [
          ...new Set([...this.dataset.entities.map((ent) => ent.text), entity]),
        ],
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.entities {
  &__container {
    &__button {
      margin-top: 0.3em;
      margin-left: 0.3em;
    }
    &--multiple {
      .entity:not(.active) {
        // opacity: 0.7;
      }
    }
  }
}
.entity {
  padding: 0.3em;
  margin: 1em 0.5em 0 0.5em;
  position: relative;
  display: inline-block;
  cursor: pointer;
  max-height: 28px;
  border: 2px solid transparent;
  transition: all 0.2s ease-in-out;
  // &:not(.active):hover {
  //   filter: brightness(90%);
  // }
  &.non-selectable,
  &.non-selectable--show-sort-code {
    cursor: default;
    pointer-events: none;
  }
  &__sort-code {
    @include font-size(12px);
    color: $font-medium-color;
    font-weight: lighter;
    margin-left: 0.5em;
    .non-selectable & {
      display: none;
    }
  }
  &__new {
    margin: 0 0 0 0.5em;
    display: inline-block;
    color: $primary-color;
    line-height: 25px;
    &:hover {
      color: darken($primary-color, 10%);
    }
    &__container {
      margin-left: 0.5em;
      position: relative;
      display: inline-block;
      .re-button {
        @include font-size(13px);
        margin-left: auto;
        margin-right: 1em;
        margin-bottom: 0.5em;
        display: block;
        color: $primary-color;
        font-weight: bold;
        &:hover,
        &:focus {
          text-decoration: none;
          color: darken($primary-color, 10%);
        }
        &:after {
          content: none !important;
        }
      }
      .svg-icon {
        cursor: pointer;
        position: absolute;
        right: 1em;
        top: 0;
        bottom: 0;
        margin: auto;
        color: $primary-color;
        &:hover {
          color: darken($primary-color, 10%);
        }
      }
    }
    &__input {
      border: 1px solid $line-smooth-color;
      min-height: 30px;
      padding: 2px 10px;
      outline: none;
    }
  }
}
// ner colors

$colors: 40;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(($colors * $i) + ($hue * $i / $colors), 100%, 82%, 1);
  .color_#{$i - 1} {
    background: $rcolor;
    &.active,
    &.entity:hover {
      border: 2px solid darken($rcolor, 50%);
    }
  }
  .entity.color_#{$i - 1} span {
    background: $rcolor;
  }
  .entities__selector__option.color_#{$i - 1} span {
    background: $rcolor;
  }
  .entities__selector__option.color_#{$i - 1} {
    background: white;
    &:hover {
      background: hsla(($colors * $i) + ($hue * $i / $colors), 100%, 97%, 1);
    }
    &:active {
      background: hsla(($colors * $i) + ($hue * $i / $colors), 100%, 94%, 1);
    }
  }
  .color_#{$i - 1} ::v-deep .highlight__tooltip {
    background: $rcolor;
  }
  .color_#{$i - 1} ::v-deep .highlight__tooltip:after {
    border-color: $rcolor transparent transparent transparent;
  }
}
</style>
