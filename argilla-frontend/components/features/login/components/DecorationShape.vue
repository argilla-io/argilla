<template>
  <svg
    width="756"
    height="444"
    viewBox="0 0 756 444"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="deco--bottom"
  >
    <path
      d="M363.973 174.466C363.973 219.289 401.487 255.625 447.763 255.625C494.039 255.625 531.554 219.289 531.554 174.466C531.554 129.644 494.039 93.3084 447.763 93.3084C401.487 93.3084 363.973 129.644 363.973 174.466Z"
      fill="#FF675F"
    />
    <path
      d="M687.779 145.647C670.068 186.608 618.51 203.843 572.479 184.099C526.448 164.355 503.401 115.119 520.872 74.0558L687.779 145.647Z"
      fill="#FF675F"
      fill-opacity="0.8"
    />
    <path
      d="M719.123 71.5916C701.412 112.552 649.853 129.787 603.823 110.043C557.792 90.2988 534.744 41.063 552.216 0L719.123 71.5916Z"
      fill="#FF675F"
      fill-opacity="0.8"
    />
    <path
      d="M736.839 310.907C700.721 370.918 622.931 390.402 562.998 354.405L509.687 442.982C449.887 406.764 430.563 328.857 466.681 268.847C502.8 208.836 580.633 189.529 640.566 225.526L693.877 136.949C753.633 172.99 772.958 250.897 736.839 310.907Z"
      fill="url(#paint0_linear_5473_2963)"
    />
    <path
      d="M182.794 344.836C182.794 399.592 227.183 443.98 281.939 443.98C336.695 443.98 381.083 399.592 381.083 344.836C381.083 290.08 336.695 245.691 281.939 245.691C227.183 245.691 182.794 290.08 182.794 344.836Z"
      fill="#FF675F"
    />
    <path
      d="M150.946 248.273C163.629 289.337 140.226 333.005 98.6011 345.983C56.9759 358.961 12.8688 336.224 0.00012207 295.336L150.946 248.273Z"
      fill="url(#paint1_linear_5473_2963)"
    />
    <path
      d="M45.9867 442.829C33.3035 401.765 56.7065 358.097 98.3316 345.119C139.957 332.141 184.064 354.878 196.933 395.766L45.9867 442.829Z"
      fill="url(#paint2_linear_5473_2963)"
    />
    <path
      d="M467.863 440.652C417.312 450.452 368.324 416.933 358.246 365.677C348.167 314.42 380.949 264.823 431.314 254.78L467.863 440.652Z"
      fill="url(#paint3_linear_5473_2963)"
    />
    <defs>
      <linearGradient
        id="paint0_linear_5473_2963"
        x1="462.019"
        y1="323.472"
        x2="308.123"
        y2="476.906"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint1_linear_5473_2963"
        x1="-489.603"
        y1="-2.82015"
        x2="-156.278"
        y2="769.073"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint2_linear_5473_2963"
        x1="462.019"
        y1="323.472"
        x2="308.123"
        y2="476.906"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint3_linear_5473_2963"
        x1="462.019"
        y1="323.472"
        x2="308.123"
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
    bottom: 0;
    right: 0;
    width: clamp(560px, 70%, 800px);
    @extend %deco;
  }
}
</style>
