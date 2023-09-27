<template>
  <div :class="isButtonActive ? 'metadata-button--active' : 'metadata-button'">
    <BaseButton class="metadata-button__button" v-if="!badges.length"
      >Metadata</BaseButton
    >
    <svgicon v-else name="filter" width="16" height="16" />
    <div class="metadata-button__badges" v-if="badges.length">
      <FilterBadge
        class="metadata-button__badge"
        :active-badge="activeBadge === badge && isActive"
        v-for="badge in visibleBadges"
        :key="badge"
        :text="badge"
        @on-click="onClickOnBadge(badge, $event)"
        @on-clear="onClickOnClear(badge, $event)"
      ></FilterBadge>
      <div
        class="metadata-button__badges__collapsed"
        v-if="badges.length > maxVisibleBadges"
        v-click-outside="{
          events: ['mousedown'],
          handler: onClickOutside,
        }"
      >
        <BaseBadge
          :text="`+ ${badges.length - maxVisibleBadges}`"
          @on-click="toggleTooltip"
        />
        <FilterTooltip v-if="visibleTooltip" class="metadata-button__tooltip">
          <FilterBadge
            class="badge"
            v-for="badge in collapsedBadges"
            :key="badge"
            :text="badge"
            @on-click="onClickOnBadge(badge, $event)"
            @on-clear="onClickOnClear(badge, $event)"
          ></FilterBadge>
        </FilterTooltip>
      </div>
    </div>
    <svgicon
      class="metadata-button__chevron"
      name="chevron-down"
      width="16"
      height="16"
    />
  </div>
</template>

<script>
import "assets/icons/chevron-down";
import "assets/icons/filter";
export default {
  props: {
    badges: {
      type: Array,
      default: [],
    },
    activeBadge: {
      type: String,
    },
    maxVisibleBadges: {
      default: 2,
    },
    isActive: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      visibleTooltip: false,
    };
  },
  computed: {
    visibleBadges() {
      return this.badges.slice(0, this.maxVisibleBadges);
    },
    collapsedBadges() {
      return this.badges.slice(this.maxVisibleBadges, this.badges.length);
    },
    isButtonActive() {
      return this.isActive || !!this.badges.length;
    },
  },
  methods: {
    onClickOnBadge(badge, e) {
      e.stopPropagation();

      this.$emit("click-on-badge", badge, e);
    },
    onClickOnClear(badge, e) {
      e.stopPropagation();

      this.$emit("click-on-clear", badge, e);
    },
    toggleTooltip(e) {
      e.stopPropagation();
      this.visibleTooltip = !this.visibleTooltip;
    },
    onClickOutside() {
      this.visibleTooltip = false;
    },
  },
};
</script>

<styles lang="scss" scoped>
.metadata-button {
  display: flex;
  gap: $base-space;
  align-items: center;
  height: $base-space * 5;
  padding: $base-space $base-space * 2;
  border-radius: $border-radius;
  background: none;
  transition: background-color 0.2s ease;
  cursor: pointer;
  &:hover,
  &--active {
    background: $black-4;
    @extend .metadata-button;
  }
  &__badges {
    display: flex;
    gap: calc($base-space / 2);
    &__collapsed {
      position: relative;
    }
  }
  &__badge :deep(.badge__text) {
    max-width: 140px;
  }
  &__button.button {
    padding: 0;
  }
  &__tooltip {
    display: flex;
    flex-direction: column;
    gap: calc($base-space / 2);
  }
}
</styles>
