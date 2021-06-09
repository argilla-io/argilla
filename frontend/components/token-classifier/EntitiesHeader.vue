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
      :class="[`color_${entity.colorId}`,
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
    showEntitySelector: false,
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
  },
};
</script>

<style lang="scss" scoped>
.entities {
  &__container {
    margin-bottom: 1em;
    padding: 0 4em;
    width: calc(100% - 120px);
    @include media(">desktopLarge") {
      width: calc(100% - 360px);
    }
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
  margin: 1em 1em 0 0;
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
