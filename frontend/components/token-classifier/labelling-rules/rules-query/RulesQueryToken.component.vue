<template>
  <CardComponent
    class="rule-query-token"
    :style="cssVars"
    v-if="componentToShow === 'SelectAnEntityComponent'"
  >
    <div class="rule-query-token__title-area">
      <h2 class="title">{{ title }}</h2>
      <span v-if="recordLength">
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
      <button @click="onClickSaveRule" :disabled="isSaveRulesDisable">
        Save Rules
      </button>
    </div>
  </CardComponent>

  <CardComponent
    class="if-there-is-no-global-entities"
    v-else-if="componentToShow === 'NoGlobalEntitiesComponent'"
  >
    <div class="if-there-is-no-global-entities__content">
      <div class="text-wrapper">
        <p class="title"><strong>This doesn't have any labels yet.</strong></p>
        <div class="show-what-to-do-text">
          <p class="item">
            To create a new rules you need at least two labels. It's highly
            recommended to also annotate some records with these lavels.
          </p>
          <p class="item">
            Go to the annotation mode to
            <a href="#" @click.prevent="onClickGoToAnnotationMode">
              create the labels and annotate some records
            </a>
          </p>
        </div>
      </div>
    </div>
    <div class="if-there-is-no-query__footer">
      <div class="manage-rules-btn">
        <button @click="onClickViewRules" :disabled="isManagedRulesBtnDisabled">
          {{ viewRulesBtnLabel }}
        </button>
      </div>
    </div>
  </CardComponent>

  <CardComponent
    class="if-there-is-no-query"
    v-else-if="componentToShow === 'NoQueryComponent'"
  >
    <div class="if-there-is-no-query__item">
      <div class="text-wrapper">
        <div class="label-icon">
          <svgicon name="weak-labeling" width="30" height="30" />
        </div>
        <p class="show-what-to-do-text">
          Create a new rule writting your query in the search box
        </p>
      </div>
    </div>
    <div class="if-there-is-no-query__footer">
      <div class="manage-rules-btn">
        <button @click="onClickViewRules" :disabled="isManagedRulesBtnDisabled">
          {{ viewRulesBtnLabel }}
        </button>
      </div>
    </div>
  </CardComponent>
</template>

<script>
import { TokenGlobalEntity } from "../../../../models/token-classification/TokenGlobalEntity.modelTokenClassification";
import ChipsComponent from "./Chips.component.vue";
import CardComponent from "@/components/base/card/Card.component.vue";

export default {
  name: "RulesQueryToken",
  components: {
    ChipsComponent,
    CardComponent,
  },
  props: {
    query: {
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
    rulesLength: {
      type: Number,
      default: () => 0,
    },
    isManagedRulesBtnDisabled: {
      type: Boolean,
      default: false,
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
    title() {
      return `${this.query}`;
    },
    viewRulesBtnLabel() {
      return this.rulesLength
        ? `View Rules (${this.rulesLength})`
        : `View Rules`;
    },
    componentToShow() {
      if (!this.query) {
        return "NoQueryComponent";
      }

      if (this.entities.length === 0) {
        return "NoGlobalEntitiesComponent";
      }

      return "SelectAnEntityComponent";
    },
  },
  methods: {
    onChipsSelection({ id }) {
      this.updateTokenGlobalEntities(id);
      this.disableSaveRulesButton();
    },
    onClickSaveRule() {
      this.$emit("on-click-save-rule");
    },
    updateTokenGlobalEntities(id) {
      let entities = TokenGlobalEntity.all();

      entities = entities.map((entity) => {
        if (entity.id !== id) {
          return { ...entity, is_activate: false };
        } else {
          return { ...entity, is_activate: !entity.is_activate };
        }
      });
      TokenGlobalEntity.insertOrUpdate({ data: entities });
    },
    disableSaveRulesButton() {
      const entities = TokenGlobalEntity.all();
      const isSelectedEntities = entities.some((entity) => entity.is_activate);
      isSelectedEntities
        ? (this.isSaveRulesDisable = false)
        : (this.isSaveRulesDisable = true);
    },
    onClickViewRules() {
      this.$emit("on-click-view-rules");
    },
    onClickGoToAnnotationMode() {
      this.$emit("on-click-go-to-annotation-mode");
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
  font-size: 1rem;
}

.if-there-is-no-global-entities {
  display: flex;
  flex-direction: column;
  gap: 2em;
  min-height: 344px;
  &__content {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    .text-wrapper {
      flex: 0.7;
      display: flex;
      flex-direction: column;
      gap: 2em;
      .show-what-to-do-text {
        display: flex;
        flex-direction: column;
      }
    }
  }
}

.if-there-is-no-query {
  display: flex;
  flex-direction: column;
  gap: 2em;
  min-height: 344px;
  min-width: 15em;
  &__item {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    .text-wrapper {
      display: flex;
      align-items: center;
      .label-icon {
        flex-basis: 50px;
      }
      .show-what-to-do-text {
        flex: 1;
      }
    }
  }
  &__footer {
    display: flex;
    justify-content: flex-end;
  }
}

.rule-query-token {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 2em;
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
