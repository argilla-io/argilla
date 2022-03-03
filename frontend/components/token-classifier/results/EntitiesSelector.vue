<template>
  <span class="entities__selector__container">
    <div class="entities__selector">
      <ul class="entities__selector__options">
        <li
          class="entities__selector__option suggestion"
          :class="[
            `color_${suggestedEntity.colorId}`,
            activeEntity === -1 ? 'active' : null,
          ]"
          v-if="suggestedEntity"
          @click="selectEntity(suggestedEntity)"
        >
          <span>{{ suggestedEntity.text }}</span>
          <span class="entity__sort-code">[space]</span>
        </li>
        <li
          class="entities__selector__option suggestion"
          :class="[
            `color_${lastSelectedEntity.colorId}`,
            activeEntity === -1 ? 'active' : null,
          ]"
          v-else-if="lastSelectedEntity.text"
          @click="selectEntity(lastSelectedEntity)"
        >
          <span>{{ lastSelectedEntity.text }}</span>
          <span class="entity__sort-code">[space]</span>
        </li>
        <li
          v-for="(entity, index) in formattedEntities"
          tabindex="0"
          :focused="activeEntity === index"
          :key="index"
          class="entities__selector__option"
          :class="[
            `color_${entity.colorId}`,
            activeEntity === index ? 'active' : null,
          ]"
          @click="selectEntity(entity)"
        >
          <span>{{ entity.text }}</span>
          <span class="entity__sort-code"
            >[{{ activeEntity === index ? "enter" : entity.shortCut }}]</span
          >
        </li>
      </ul>
    </div>
  </span>
</template>

<script>
import { mapActions } from "vuex";
export default {
  data: () => ({
    activeEntity: -1,
  }),
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    token: {
      type: Object,
      required: true,
    },
    suggestedLabel: {
      type: String,
    },
    formattedEntities: {
      type: Array,
    },
    showEntitiesSelector: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    lastSelectedEntity() {
      return this.dataset.lastSelectedEntity;
    },
    suggestedEntity() {
      return this.formattedEntities.find(
        (ent) => ent.text === this.suggestedLabel
      );
    },
  },
  mounted() {
    window.addEventListener("keydown", this.keyDown);
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
  },
  methods: {
    ...mapActions({
      updateLastSelectedEntity:
        "entities/token_classification/updateLastSelectedEntity",
    }),
    async selectEntity(entityLabel) {
      await this.updateLastSelectedEntity({
        dataset: this.dataset,
        lastSelectedEntity: entityLabel,
      });
      this.token.entity
        ? this.$emit("changeEntityLabel", this.token.entity, entityLabel.text)
        : this.$emit("selectEntity", entityLabel.text);
      this.resetActiveEntity();
    },
    resetActiveEntity() {
      this.activeEntity = -1;
    },
    keyDown(event) {
      const cmd = String.fromCharCode(event.keyCode).toUpperCase();
      if (this.showEntitiesSelector && cmd) {
        const element = document.getElementsByClassName("active");
        event.preventDefault();
        // enter
        if (event.keyCode === 13) {
          if (this.activeEntity !== -1) {
            this.selectEntity(this.formattedEntities[this.activeEntity]);
          }
          //space
        } else if (event.keyCode === 32) {
          if (this.suggestedEntity) {
            this.selectEntity(this.suggestedEntity);
          } else if (this.lastSelectedEntity) {
            this.selectEntity(this.lastSelectedEntity);
          }
          //down
        } else if (
          event.keyCode === 40 &&
          this.activeEntity + 1 < this.formattedEntities.length
        ) {
          this.activeEntity++;
          if (element[0] && element[0].offsetTop >= 90) {
            element[0].parentNode.scrollTop = element[0].offsetTop - 2;
          }
          //up
        } else if (event.keyCode === 38 && this.activeEntity >= 0) {
          this.activeEntity--;
          if (element[0]) {
            element[0].parentNode.scrollTop =
              element[0].offsetTop - element[0].offsetHeight - 8;
          }
        } else {
          const entity = this.formattedEntities.find((t) => t.shortCut === cmd);
          if (entity) {
            this.selectEntity(entity);
          }
        }
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.entities {
  &__selector {
    min-width: 220px;
    background: palette(grey, smooth);
    font-weight: 600;
    padding: 0.8em;
    border-radius: 1px;
    &__container {
      @include font-size(14px);
      line-height: 1em;
      display: inline-block;
      white-space: pre-line;
      position: absolute;
      left: -30%;
      top: 2em;
      z-index: 9;
    }
    &__options {
      max-height: 142px;
      overflow-y: scroll;
      padding-left: 0;
      margin: 0;
      overscroll-behavior: contain;
      position: relative;
    }
    &__option {
      display: flex;
      transition: all 0.2s ease;
      padding: 0.5em;
      position: relative;
      cursor: pointer;
      margin-top: 2px;
      margin-bottom: 2px;
      &.suggestion {
        margin-bottom: 0.5em;
      }
      span {
        cursor: pointer !important;
      }
    }
  }
}
.entity {
  &.non-selectable,
  &.non-selectable--show-sort-code {
    cursor: default;
    pointer-events: none;
  }
  &__sort-code {
    margin-left: auto;
    margin-right: 0;
    .non-selectable & {
      display: none;
    }
  }
}
</style>
