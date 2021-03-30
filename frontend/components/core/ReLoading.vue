<template>
  <div class="loading">
    <div class="spinner">
      <svgicon name="hipo" width="auto" height="80" class="icon" />
    </div>
  </div>
</template>

<script>
import "assets/icons/hipo";

export default {
  methods: {},
};
</script>

<style lang="scss" scoped>
.loading {
  background: $lighter-color;
  height: 100vh;
  width: 100vw;
  z-index: 1;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
.spinner {
    width: 130px;
    height: 130px;
    position: relative;
    margin: auto;
    text-align: center;
    display: flex;
    position: absolute;
    bottom: 0;
    top: 0;
    right: 0;
    left: 0;
    z-index: 9999;
    &:after {
        content: '';
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background-color: $secondary-lighter-color;
        opacity: 0.15;
        position: absolute;
        top: 0;
        left: 0;
        -webkit-animation: sk-bounce 2.0s infinite ease-in-out;
        animation: sk-bounce 2.0s infinite ease-in-out;
    }
    .icon {
        display: block;
        margin: auto;
        z-index: 1;
        fill: $secondary-lighter-color !important;
        -webkit-animation: sk-bounce-icon 2.0s infinite ease-in-out;
        animation: sk-bounce-icon 2.0s infinite ease-in-out;
        -webkit-animation-delay: -1s;
        animation-delay: -1s;
    }
}

.loading--content {
    @include media('>desktop') {
        left: 220px;
    }
}

.loading--inverse {
    &.spinner:after {
        background-color: #9ce4e1;
    }
    .icon {
        fill: $secondary-color;
    }
}

@keyframes sk-bounce {
    0%,
    100% {
        transform: scale(0.9);
    }
    50% {
        transform: scale(1.0);
    }
}

@keyframes sk-bounce-icon {
    0%,
    100% {
        transform: scale(0.7);
    }
    50% {
        transform: scale(0.75);
    }
}
</style>
