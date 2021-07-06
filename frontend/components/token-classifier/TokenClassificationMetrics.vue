<template>
  <div>
    <p><svgicon name="metrics" width="24" height="24" color="#4C4EA3" /> Mentions</p>
    <div class="sidebar__tabs">
      <a href="#" :class="activeTab === 'mentions' ? 'active' : ''" @click.prevent="filteredMentionsBy('mentions')">Annotated as</a>
      <a href="#" :class="activeTab === 'predicted_mentions' ? 'active' : ''" @click.prevent="filteredMentionsBy('predicted_mentions')">Predicted as</a>
    </div>
    <div class="scroll">
      <div v-for="(prop, key) in filteredMentions" :key="key" :class="expandedMentionsGroup === key ? 'expanded' : ''">
        <span :class="[`color_${entities.filter(e => e.text === key)[0].colorId}`, 'entity']">{{ key }}</span>
        <SidebarCollapsableMentions :limit="expandedMentionsGroup && expandedMentionsGroup !== key ? 0 : currentMentionsLength" :entities="entities" :k="key" :object="filteredMentions" @limit="onShowMore(key)" />
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    limit: 3,
    currentMentionsLength: 3,
    visible: false,
    activeTab: 'mentions',
    filteredMentions: [],
    expandedMentionsGroup: undefined,
  }),
  computed: {
    datasetName() {
      return this.dataset.name;
    },
    entities() {
      return this.dataset.entities;
    }
  },

  watch: {
    async datasetName() {
      this.$fetch();
    },
  },

  methods: {
    filteredMentionsBy(type) {
      this.activeTab = type;
      this.filteredMentions = this.dataset.results.aggregations[type];
      this.expandedMentionsGroup = undefined;
      this.currentMentionsLength = this.limit;
    },
    onShowMore(k) {
      const itemsLenght = Object.keys(this.filteredMentions[k]).length;
      this.currentMentionsLength === this.limit ? this.currentMentionsLength = itemsLenght : this.currentMentionsLength = this.limit;
      this.currentMentionsLength === itemsLenght ? this.expandedMentionsGroup = k : this.expandedMentionsGroup = undefined;
    },
  },
  mounted() {
    this.filteredMentions = this.dataset.results.aggregations[this.activeTab];
  }
};
</script>
<style lang="scss" scoped>
.sidebar {
  &__tabs {
    display: flex;
    padding-bottom: 1em;
    a {
      width: 100%;
      border: 1px solid palette(grey, smooth);
      border-radius: 2px;
      text-align: center;
      color: $font-secondary;
      text-decoration: none;
      margin: 0 5px;
      @include font-size(13px);
      padding: 0.3em;
      &.active {
        background: palette(grey, light);
      }
    }
  }
  p {
    display: flex;
    align-items: flex-end;
    font-size: 18px;
    font-size: 1.125rem;
    margin-top: 0;
    margin-bottom: 2em;
    font-weight: 600;
    svg {
      margin-right: 0.5em;
    }
  }
  .entity {
    margin-top: 1em;
    margin-bottom: 0.5em;
    padding: 0.5em;
    display: inline-flex;
  }
  .scroll {
    max-height: calc(100vh - 400px);
    padding-right: 1em;
    margin-right: -1em;
    overflow: auto;
  }
}
$colors: 40;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(($colors * $i) + ($hue * $i / $colors), 100%, 82%, 1);
  .color_#{$i - 1} {
    background: $rcolor;
  }
}
</style>
 