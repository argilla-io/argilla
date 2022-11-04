<template>
  <div class="rule-query-token" :style="cssVars">
    <div class="rule-query-token__title-area">
      <h2 class="title" v-text="title">{{ title }}</h2>
      <span>
        Records: <b>{{ recordLength }}</b>
      </span>
    </div>
    <div class="rule-query-token__search">
      <BaseInputContainer class="searchbar">
        <svgicon v-if="!searchEntity" name="search" width="20" height="40" />
        <svgicon
          class="searchbar__button"
          v-else
          name="close"
          width="20"
          height="20"
          @click="searchEntity = ''"
        />
        <BaseInput
          v-model="searchEntity"
          class="searchbar__input"
          placeholder="Search an entity"
        />
      </BaseInputContainer>
    </div>
    <div class="rule-query-token__chips">
      <ChipsComponent :chips="entities" @on-chips-select="onChipsSelection" />
    </div>
    <div class="rule-query-token__save-rules-button">
      <button @click="onSaveRules" :disabled="isSaveRulesDisable">
        Save Rules
      </button>
    </div>
  </div>
</template>

<script>
import { TokenEntity } from "../../../../models/token-classification/TokenEntity.modelTokenClassification";
import ChipsComponent from "./Chips.component.vue";
export default {
  name: "RulesQueryToken",
  components: {
    ChipsComponent,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    entities: {
      type: Array,
      required: true,
    },
    recordLength: {
      type: Number | null,
      default: () => null,
    },
    textColor: {
      type: String,
      default: () => "#000",
    },
    backgroundColor: {
      type: String,
      default: () => "#fff",
    },
    backgroundLabelColor: {
      type: String,
      default: () => "#fff",
    },
  },
  data() {
    return {
      selectedEntity: [],
      isSaveRulesDisable: true,
      searchEntity: "",
    };
  },
  computed: {
    cssVars() {
      return {
        "--text-color": this.textColor,
        "--background-color": this.backgroundColor,
        "--background-label-color": this.backgroundLabelColor,
      };
    },
  },
  methods: {
    onChipsSelection({ id }) {
      this.updateTokenEntities(id);
      this.disableSaveRulesButton();
    },
    onSaveRules() {
      console.log("newEntities", this.selectedEntity);
    },
    updateTokenEntities(id) {
      let entities = TokenEntity.all();
      entities = entities.map((entity) => {
        if (entity.id !== id) {
          return { ...entity, is_activate: false };
        } else {
          return { ...entity, is_activate: !entity.is_activate };
        }
      });
      TokenEntity.insertOrUpdate({ data: entities });
    },
    disableSaveRulesButton() {
      const entities = TokenEntity.all();
      const isSelectedEntities = entities.some((entity) => entity.is_activate);
      isSelectedEntities
        ? (this.isSaveRulesDisable = false)
        : (this.isSaveRulesDisable = true);
    },
  },
  watch: {
    searchEntity(newValue) {
      this.$emit("on-search-entity", newValue);
    },
  },
};
</script>

<style lang="scss" scoped>
* {
  margin: inherit;
}
.rule-query-token {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 2em;
  gap: 2em;
  color: var(--text-color);
  background-color: var(--background-color);
  border: 1px solid #e9eaed;
  border-radius: 10px;
  &__title-area {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: baseline;
    .title {
      padding-bottom: 0;
      margin-top: 0;
      @include font-size(22px);
      line-height: 22px;
      font-weight: bold;
    }
  }
  &__search {
    .searchbar {
      display: flex;
      gap: 1em;
      align-items: center;
    }
  }
  &__chips {
    display: flex;
    flex-direction: row;
    gap: 10px;
  }
}

.searchbar__button {
  cursor: pointer;
}
</style>
