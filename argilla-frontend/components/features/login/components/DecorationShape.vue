<template>
  <svg
    class="deco--bottom"
    width="802"
    height="444"
    viewBox="0 0 802 444"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <ellipse
      cx="48.5"
      cy="47"
      rx="48.5"
      ry="47"
      transform="matrix(-1 0 0 1 97 349.098)"
      fill="#FF675F"
    />
    <ellipse
      cx="83.7902"
      cy="81.1581"
      rx="83.7902"
      ry="81.1581"
      transform="matrix(-1 0 0 1 577.583 93.3083)"
      fill="#FF675F"
    />
    <path
      d="M733.808 145.647C716.097 186.608 664.539 203.843 618.508 184.099C572.477 164.355 549.43 115.119 566.901 74.0559L733.808 145.647V145.647Z"
      fill="#FF675F"
      fill-opacity="0.8"
    />
    <path
      d="M765.152 71.5916C747.441 112.552 695.882 129.787 649.851 110.043C603.82 90.2988 580.773 41.063 598.245 -7.71229e-06L765.152 71.5916V71.5916Z"
      fill="#FF675F"
      fill-opacity="0.8"
    />
    <path
      d="M782.868 310.908C746.75 370.918 668.96 390.402 609.027 354.405L555.716 442.982C495.916 406.764 476.592 328.858 512.71 268.847C548.828 208.836 626.662 189.529 686.595 225.526L739.906 136.949C799.662 172.99 818.987 250.897 782.868 310.908Z"
      fill="#FF675F"
    />
    <path
      d="M228.823 344.836C228.823 399.592 273.211 443.98 327.967 443.98C382.723 443.98 427.112 399.592 427.112 344.836C427.112 290.08 382.723 245.691 327.967 245.691C273.211 245.691 228.823 290.08 228.823 344.836Z"
      fill="#FF675F"
    />
    <path
      d="M196.975 248.273C209.658 289.337 186.255 333.005 144.63 345.983C103.005 358.961 58.8978 336.224 46.0292 295.336L196.975 248.273Z"
      fill="url(#paint0_linear_5486_3039)"
    />
    <path
      d="M92.0156 442.829C79.3323 401.765 102.735 358.097 144.36 345.119C185.986 332.141 230.093 354.878 242.961 395.766L92.0156 442.829Z"
      fill="url(#paint1_linear_5486_3039)"
    />
    <path
      d="M513.891 440.652C463.341 450.452 414.353 416.933 404.275 365.677C394.196 314.42 426.978 264.823 477.343 254.78L513.891 440.652Z"
      fill="url(#paint2_linear_5486_3039)"
    />
    <defs>
      <linearGradient
        id="paint0_linear_5486_3039"
        x1="236.059"
        y1="370.253"
        x2="94.8838"
        y2="256.365"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint1_linear_5486_3039"
        x1="188.725"
        y1="427.43"
        x2="47.5502"
        y2="313.542"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint2_linear_5486_3039"
        x1="508.048"
        y1="323.472"
        x2="354.152"
        y2="476.906"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
    </defs>
  </svg>
</template>

<style lang="scss" scoped>
%deco {
  display: none;
  @include media(">desktop") {
    display: block;
    position: absolute;
    height: auto;
  }
}
.deco {
  &--bottom {
    right: 0;
    bottom: 0;
    width: clamp(560px, 70%, 800px);
    @extend %deco;
  }
}
</style>
