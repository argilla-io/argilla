<template>
  <div class="draggable">
    <draggable
      class="draggable__questions-container"
      :list="ranking.questions"
      :group="{ name: 'question' }"
      :sort="false"
    >
      <div
        v-for="{ text, value } in ranking.questions"
        :key="value"
        class="draggable__rank-card--unranked"
        :title="text"
      >
        <svgicon width="6" name="draggable" />
        <span class="draggable__rank-card__title" v-text="text" />
      </div>
    </draggable>

    <div class="draggable__slots-container">
      <div
        class="draggable__slot"
        :class="{ '--active-slot': items.length }"
        v-for="{ index, rank, items } in ranking.slots"
        :key="index"
      >
        <span class="draggable__slot-box--ranking" v-text="rank" />
        <draggable
          class="draggable__slot-box"
          :list="items"
          group="question"
          :sort="false"
          @add="onMoveEnd"
          @remove="onMoveEnd"
        >
          <div
            v-for="{ text, value } in items"
            :key="value"
            class="draggable__rank-card--ranked"
            :title="text"
          >
            <svgicon width="6" name="draggable" />
            <span class="draggable__rank-card__title" v-text="text" />
          </div>
        </draggable>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/draggable";
export default {
  name: "DndSelectionComponent",
  props: {
    ranking: {
      type: Object,
      required: true,
    },
  },
  methods: {
    onMoveEnd() {
      this.$emit("on-reorder", this.ranking);
    },
  },
};
</script>

<style lang="scss" scoped>
$card-primary-color: palette(purple, 200);
$card-secondary-color: palette(white);
$card-ghost-color: palette(purple, 300);
$card-empty-color: palette(purple, 400);
$cards-separation: $base-space;
$background-slot-color: $black-4;
$slot-height: 50px;
$card-height: $base-space * 4;
$max-visible-card-items: 12;

.draggable {
  user-select: none;
  display: flex;
  flex-direction: row-reverse;
  gap: $base-space;
  &__questions-container {
    display: flex;
    flex-direction: column;
    gap: $cards-separation;
    width: 40%;
    min-width: 0;
    max-height: ($card-height + $base-space) * $max-visible-card-items;
    padding: 2px;
    overflow: auto;
  }

  &__slots-container {
    width: 60%;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: $cards-separation;
  }

  &__slot {
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: stretch;
    justify-items: center;
    gap: $base-space;
  }

  &__rank-card {
    height: $card-height;
    min-width: 50px;
    display: flex;
    align-items: center;
    gap: $base-space;
    padding: $base-space;
    border-radius: $border-radius;
    cursor: move;
    &[draggable="true"] {
      background: $card-ghost-color;
      color: $card-primary-color;
      box-shadow: $shadow-500;
    }
    &.ghost-ticket {
      background: $card-empty-color;
      color: $card-empty-color;
      box-shadow: none;
    }
    &.sortable-ghost {
      background: $card-empty-color;
      color: $card-empty-color;
      box-shadow: none;
      &:hover {
        box-shadow: none;
      }
    }
    &--unranked {
      @extend .draggable__rank-card;
      background-color: $card-secondary-color;
      color: $card-primary-color;
      transition: box-shadow 0.2s ease-out;
      &:hover {
        box-shadow: $shadow-100;
        transition: box-shadow 0.2s ease-in;
      }
    }
    &--ranked {
      @extend .draggable__rank-card;
      background-color: $card-primary-color;
      color: palette(white);
    }
    &__title {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 500;
    }
  }

  &__slot-box {
    width: calc(100% - $base-space * 6);
    min-height: $slot-height;
    display: flex;
    flex-direction: column;
    gap: calc($base-space / 2);
    padding: $base-space;
    background-color: $background-slot-color;
    border-radius: $border-radius;
    border: 1px solid transparent;
    @supports (selector(:has(*))) {
      &:has([draggable="true"]) {
        border: 1px dashed $black-10;
      }
    }
    &--ranking {
      @extend .draggable__slot-box;
      max-width: $slot-height;
      align-items: center;
      justify-content: space-around;
      border-color: $black-10;
      font-weight: bold;
      color: $black-54;
      .--active-slot & {
        border-color: #cdcdff;
      }
    }
  }

  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
