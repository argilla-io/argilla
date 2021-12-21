<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <div class="error">
    <div class="container">
      <div class="error__content">
        <p class="error__text">
          Oh no!
          <br />It looks like we’ve been split up
        </p>
        <h1 v-if="error.statusCode === 404">Error 404</h1>
        <h1 v-else class="error__title">An error occurred</h1>
        <p class="error__subtitle">
          The page you’re looking for can’t be found.
        </p>
        <NuxtLink to="/" class="error__link">Take me home</NuxtLink>
      </div>
    </div>
    <div class="error--bg">
      <svg
        width="1461px"
        height="421px"
        viewBox="0 0 1461 421"
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
      >
        <g
          id="*-Documentation"
          stroke="none"
          stroke-width="1"
          fill="none"
          fill-rule="evenodd"
        >
          <g
            id="error-message-explore"
            transform="translate(0.000000, -392.000000)"
          >
            <path
              id="Path-2"
              d="M858.516319,553.275608 L979.678991,553.275608 C981.110745,541.1066 988.964344,535.022095 1003.23979,535.022095 C1024.65295,535.022095 1026.12972,558.684553 1034.99035,549.412076 C1043.85097,540.139599 1036.71266,529.771294 1041.71561,510.522956 C1046.71857,491.274618 1069.69015,503.68286 1074.12475,510.522956 C1076.38052,514.002333 1060.81308,530.311269 1059.72624,530.311269 C1058.24804,530.311269 1069.69015,522.367351 1074.12475,526.230883 C1078.55935,530.094415 1036.42637,549.412076 1078.55506,549.412076 C1120.68375,549.412076 1282.26499,553.275608 1362.05275,553.275608 C1415.24459,553.275608 1454.88531,557.654278 1480.97492,566.411617 C1454.3974,588.92992 1431.73073,601.126048 1412.97492,603 C1298.76247,614.411322 1138.55263,593 951.974916,593 C855.308249,602.333333 824.155383,589.091869 858.516319,553.275608 Z"
              fill="#FFB493"
              transform="translate(1162.987458, 553.293021) scale(-1, 1) translate(-1162.987458, -553.293021) "
            />
            <path
              id="Path-2"
              d="M-53.8848338,566.411617 C-21.8848338,566.411617 486.348425,557.911847 493.739424,553.275608 C501.130422,548.639369 502.479959,545.067279 503.219058,535.022095 C503.958158,524.976912 482.541418,519.022727 485.497817,510.522956 C488.454217,502.023185 472.326257,475.236893 485.497817,475.236893 C490.696306,475.236893 496.652685,473.050991 502.228207,471.267352 C510.779544,468.531733 518.434981,466.742365 521.086118,475.236893 C525.465812,489.269902 533.501423,516.046163 524.632225,510.522956 C515.763027,504.999749 507.043221,512.55069 512.21692,519.390786 C517.390619,526.230883 533.650816,512.322167 521.086118,526.230883 C508.521421,540.139599 527.939231,549.412076 534.969616,549.412076 C542,549.412076 580.405242,553.275608 660.193,553.275608 C713.384839,553.275608 753.025561,557.654278 779.115166,566.411617 C449.652192,582.137206 168.652192,590 -63.8848338,590 C-131.579295,590 -89.8848338,566.411617 -53.8848338,566.411617 Z"
              fill="#FFB493"
            />
            <path
              id="Rectangle-7"
              d="M1,582 C437.800642,571.552576 696.133975,566.219243 776,566 C793.854245,565.950988 794.444815,491.443886 784,474 C774.223177,457.671727 719,419 759,434 C792.39464,446.52299 794.387945,434 805,434 C815.451449,434 828.950628,454.899462 844,442 C855.594238,432.062082 880,423 887,442 C894,461 887,469 876,474 C842.354395,489.293457 839,526 851,564 C859,589.333333 1062.66667,595.333333 1462,582 L1462,921 L1,921 L1,582 Z"
              fill="#89D8F1"
            />
            <ellipse
              id="eye-1"
              fill="#FBFAED"
              cx="512.5"
              cy="486.5"
              rx="2.5"
              ry="4.5"
            />
            <path
              id="Path-3"
              d="M897,405 C909,391.666667 917,388.666667 921,396 C925,403.333333 917,406.333333 897,405 Z"
              fill="#89D8F1"
            />
            <path
              id="Path-4"
              d="M889,427 C901,431 907,436.333333 907,443 C907,453 931,458 936,443 C941,428 936,416 916,418 C902.666667,419.333333 893.666667,422.333333 889,427 Z"
              fill="#89D8F1"
            />
            <path
              id="Path-5"
              d="M730,435.859375 C713.814815,436.286458 708.185185,440.583333 713.111111,448.75 C718.037037,456.916667 723.666667,452.619792 730,435.859375 Z"
              fill="#89D8F1"
            />
            <ellipse
              id="eye-2"
              fill="#FBFAED"
              transform="translate(1265.000000, 514.000000) rotate(46.000000) translate(-1265.000000, -514.000000) "
              cx="1265"
              cy="514"
              rx="2"
              ry="3"
            />
          </g>
        </g>
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  layout: "error",
  props: ["error"],
};
</script>
<style lang="scss" scoped>
@import url("https://fonts.googleapis.com/css2?family=Just+Me+Again+Down+Here&display=swap");
.container {
  @extend %container;
}
.navbar {
  border-bottom: 1px solid $line-light-color;
  display: block;
  svg {
    max-width: 120px;
    height: auto;
    padding: 1em;
  }
}
.error {
  position: relative;
  min-height: calc(100vh - 8em);
  background-size: 100%;
  background: $lighter-color;
  &__content {
    max-width: 700px;
    margin: auto;
  }
  &--bg {
    position: absolute;
    width: 100%;
    bottom: -8em;
    pointer-events: none;
    svg {
      width: 100%;
      height: auto;
      display: block;
    }
  }
  &__link {
    color: $primary-color;
    text-decoration: none;
    @include font-size(18px);
    &:hover {
      text-decoration: underline;
    }
  }
  &__title {
    display: block;
    margin-right: 1em;
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 1em;
    @include font-size(32px);
    line-height: 1.2em;
  }
  &__subtitle {
    display: block;
    font-weight: lighter;
    margin-top: 0 !important;
    margin-bottom: 1em;
    color: $darker-color;
    @include font-size(32px);
    line-height: 1.2em;
  }
  &__text {
    font-family: "Just Me Again Down Here";
    color: #4c10bc;
    font-size: 4.2rem;
    line-height: 0.8em;
    margin-top: 0;
    margin-bottom: 0.5em;
  }
  &__links {
    font-weight: bold;
    list-style: none;
    text-decoration: none;
    padding-left: 0;
    li {
      margin-bottom: 1em;
    }
    a {
      text-decoration: none;
      @include font-size(15px);
    }
    .svg-icon {
      margin-left: 0.5em;
    }
  }
  ::v-deep .footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
  }
}
#eye-1 {
  animation: animateEye1 3s infinite 3s;
}
#eye-2 {
  animation: animateEye2 3s infinite;
}
@keyframes animateEye1 {
  0% {
    ry: 4.5;
  }
  5% {
    ry: 0;
  }
  10% {
    ry: 4.5;
  }
  100% {
    ry: 4.5;
  }
}
@keyframes animateEye2 {
  0% {
    ry: 3.5;
  }
  5% {
    ry: 0;
  }
  10% {
    ry: 3.5;
  }
  100% {
    ry: 3.5;
  }
}
</style>
