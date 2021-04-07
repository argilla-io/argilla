<template>
  <div class="help">
    <div class="help__button" v-if="!showHelpPanel" @click="showHelpPanel = true">
      <svgicon
        name="help"
        width="22"
        height="22"
        color="#F38959"
      ></svgicon>
        Help
    </div>
    <div class="help__panel" v-if="showHelpPanel">
      <div class="help__panel__button" @click="showHelpPanel = false">
        Close
      </div>
      <p class="help__panel__title" >What do highlight colours mean?</p>
      <p>We use model interpretability methods such as Integrated Gradients to compute the attribution of tokens to the model prediction with the goal of providing hints about the model interpretation of data.</p>
      <p>Model predictions can be correct or incorrect, as indicated by the green or red labels assigned to the predictions together with their confidence. Given this attributions work as follows:</p>
      <p>[0,+1] <strong>Positive attributions</strong> will have the same colour as the label assigned to the prediction (red for wrong, green for correct). Tokens with positive attributions have the most impacto on the model predicting a specific label.</p>
      <p>[1-, 0] <strong>Negative attributions</strong> will always be blue and highlight those tokens that diverge the model from its final prediction.</p>
    </div>
  </div>
</template>

<script>
export default {
  data: () => ({
    showHelpPanel: false
  })
}
</script>

<style lang="scss" scoped>
.help {
  clear: both;
  margin-top: 1em;
  .fixed-header & {
    display: none;
  }
  &__panel {
    border: 1px solid #f48e5f57;
    padding: 3em 2em 0.5em 2em;
    background: #ffffff87;
    color: palette(grey, medium);
    border-radius: 1px;
    position: relative;
    .atom {
      @include font-size(16px);
      display: inline-block;
    }
    &__title {
      @include font-size(16px);
      color: palette(grey, medium);
      font-weight: 600;
      margin-top: 0;
    }
    ul, p {
      @include font-size(13px);
    }
    ul {
      padding-left: 1.5em;
      margin-bottom: 1.5em;
    }
    &__button {
      color: palette(orange);
      position: absolute;
      right: 1em;
      top: 1em;
      cursor: pointer;
      &:after {
        content: '\2715';
        font-weight: bold;
        color: palette(orange);
        font-size: 14px;
      }
    }
  }
  &__button {
    text-align: right;
    color: palette(orange);
    font-weight: 600;
    cursor: pointer;
    .svg-icon {
      margin-right: 0.3em;
    }
  }
}
</style>

