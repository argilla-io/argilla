<template>
  <div class="text_field_component" :key="fieldText">
    <div class="title-area --body2">
      <span class="text_field_component__title-content" v-text="title" />
      <BaseActionTooltip
        class="text_field_component__tooltip"
        tooltip="Copied"
        tooltip-position="left"
      >
        <BaseButton
          title="Copy to clipboard"
          class="text_field_component__copy-button"
          @click.prevent="$copyToClipboard(fieldText)"
        >
          <svgicon color="#acacac" name="copy" width="18" height="18" />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <div :id="`fields-content-${name}`" class="content-area --body1">
      <div :class="classes" v-if="!useMarkdown" v-html="fieldText" />
      <Sandbox v-else :fieldText="example3" :record="record" />
      <template>
        <style :key="name" scoped>
          ::highlight(search-text-highlight-{{name}}) {
            color: #ff675f;
          }
        </style>
      </template>
    </div>
  </div>
</template>

<script>
import { useTextFieldViewModel } from "./useTextFieldViewModel";

export default {
  name: "TextFieldComponent",
  props: {
    name: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    searchText: {
      type: String,
      default: "",
    },
    fieldText: {
      type: String,
      required: true,
    },
    useMarkdown: {
      type: Boolean,
      default: false,
    },
    record: {
      type: Object,
    },
  },
  data() {
    return {
      example1: `<link href="https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist/flowbite.min.css" rel="stylesheet" />
<style>
    body {
      background-color: #E20074
    }

    .bg-telekom-magenta {
        background-color: #E20074
    }
</style>

<div class="flex-1 p:2 sm:p-6 justify-between flex flex-col">
<div id="messages" class="flex flex-col space-y-4 p-3 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch">
<div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

<div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

</div>
</div>

<h2 class="ml-2">Vue JS</h2>

<script src="https://unpkg.com/vue@3/dist/vue.global.js"><\/script>

<div id="app">
  <p class="ml-2">{{ message }}</p>

  <input type="text" v-model="message" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="John" required />

  <br />

  <button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800" @click="counter++">+</button>

  {{counter}}

  <button type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800" @click="counter--">-</button>

  <h3>Data</h3>

  {{ JSON.stringify(fromOutside) }}
</div>

<script>
  const { createApp, ref } = Vue

  createApp({
    setup() {
      const message = ref('Hello vue!')
      const counter = ref(0)
      const fromOutside = ref("NONE")

      window.addEventListener('message', ({data})=>  {
        fromOutside.value = JSON.parse(data);
      });

      return {
        message,
        counter,
        fromOutside
      }
    }
  }).mount('#app')
<\/script>
`,

      example2: `


		<style>
			body {
				background-color: #bfe3dd;
				color: #000;
			}

			a {
				color: #2983ff;
			}
		</style>

		<div id="container"></div>

<script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@latest/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@latest/examples/jsm/"
    }
  }
<\/script>

<script type="module">

			import * as THREE from 'three';

			import Stats from 'three/addons/libs/stats.module.js';

			import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
			import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

			import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
			import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

			let mixer;

			const clock = new THREE.Clock();
			const container = document.getElementById( 'container' );

			const stats = new Stats();
			container.appendChild( stats.dom );

			const renderer = new THREE.WebGLRenderer( { antialias: true } );
			renderer.setPixelRatio( window.devicePixelRatio );
			renderer.setSize( window.innerWidth, window.innerHeight );
			container.appendChild( renderer.domElement );

			const pmremGenerator = new THREE.PMREMGenerator( renderer );

			const scene = new THREE.Scene();
			scene.background = new THREE.Color( 0xbfe3dd );
			scene.environment = pmremGenerator.fromScene( new RoomEnvironment( renderer ), 0.04 ).texture;

			const camera = new THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 100 );
			camera.position.set( 5, 2, 8 );

			const controls = new OrbitControls( camera, renderer.domElement );
			controls.target.set( 0, 0.5, 0 );
			controls.update();
			controls.enablePan = false;
			controls.enableDamping = true;

			const dracoLoader = new DRACOLoader();
			dracoLoader.setDecoderPath( ' http://localhost:8081/jsm/libs/draco/gltf/' );

			const loader = new GLTFLoader();
			loader.setDRACOLoader( dracoLoader );
			loader.load( ' http://localhost:8080/models/gltf/LittlestTokyo.glb', function ( gltf ) {

				const model = gltf.scene;
				model.position.set( 1, 1, 0 );
				model.scale.set( 0.01, 0.01, 0.01 );
				scene.add( model );

				mixer = new THREE.AnimationMixer( model );
				mixer.clipAction( gltf.animations[ 0 ] ).play();

				renderer.setAnimationLoop( animate );

			}, undefined, function ( e ) {

				console.error( e );

			} );


			window.onresize = function () {

				camera.aspect = window.innerWidth / window.innerHeight;
				camera.updateProjectionMatrix();

				renderer.setSize( window.innerWidth, window.innerHeight );

			};


			function animate() {

				const delta = clock.getDelta();

				mixer.update( delta );

				controls.update();

				stats.update();

				renderer.render( scene, camera );

			}


		<\/script>




`,

      example3: `

      <div id="container"></div>

	  <script src="http://localhost:8082/bower_components/three.js/three.min.js"><\/script>
		<script src="http://localhost:8082/STLLoader.js"><\/script>
    <script src='http://localhost:8082/TrackballControls.js'><\/script>

		<script>

			

			var camera, cameraTarget, scene, renderer;

			init();
			animate();

			function init() {

        const container = document.getElementById( 'container' );

				camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 1, 15);
				camera.position.set(3, 5, 3);

        // MOUSE CONTROLS
        controls = new THREE.TrackballControls(camera);
	      controls.rotateSpeed = 2.0;
				controls.zoomSpeed = 2.2;
				controls.panSpeed = 0.8;
				controls.noZoom = false;
				controls.noPan = false;
				controls.staticMoving = true;
				controls.dynamicDampingFactor = 0.3;
				controls.keys = [65, 83, 68];
				controls.addEventListener('change', render);
				cameraTarget = new THREE.Vector3(0, -0.25, 0);

				scene = new THREE.Scene();

				var loader = new THREE.STLLoader();
				var material = new THREE.MeshPhongMaterial({color: 0xAAAAAA, specular: 0xffffff, shininess: 100});

				loader.load('http://localhost:8082/stl/STEP3.stl', function (geometry) {
					var mesh = new THREE.Mesh(geometry, material);
					mesh.scale.set(0.02, 0.02, 0.02);
					scene.add(mesh);
				});

				// LIGHTS
				scene.add( new THREE.HemisphereLight(0xffffff, 0x111122));

				// RENDERER
				renderer = new THREE.WebGLRenderer({antialias: true});
				renderer.setPixelRatio(window.devicePixelRatio);
				renderer.setSize(window.innerWidth, window.innerHeight);

				renderer.gammaInput = true;
				renderer.gammaOutput = true;

				container.appendChild(renderer.domElement);


				window.addEventListener('resize', onWindowResize, false);

			}

			function onWindowResize() {
				camera.aspect = window.innerWidth / window.innerHeight;
				camera.updateProjectionMatrix();
				renderer.setSize(window.innerWidth, window.innerHeight);
        controls.handleResize();
			}

			function animate() {
				requestAnimationFrame(animate);
				render();
        controls.update();
			}

			var debugaxis = function(axisLength){
			    //Shorten the vertex function
			    function v(x,y,z){
			            return new THREE.Vertex(new THREE.Vector3(x,y,z));
			    }

			    //Create axis (point1, point2, colour)
			    function createAxis(p1, p2, color){
			            var line, lineGeometry = new THREE.Geometry(),
			            lineMat = new THREE.LineBasicMaterial({color: color, lineWidth: 1});
			            lineGeometry.vertices.push(p1, p2);
			            line = new THREE.Line(lineGeometry, lineMat);
			            scene.add(line);
			    }

			    createAxis(v(-axisLength, 0, 0), v(axisLength, 0, 0), 0xFF0000);
			    createAxis(v(0, -axisLength, 0), v(0, axisLength, 0), 0x00FF00);
			    createAxis(v(0, 0, -axisLength), v(0, 0, axisLength), 0x0000FF);
			};

			//To use enter the axis length
			debugaxis(100);

			function render() {
				camera.lookAt(cameraTarget);
				renderer.render(scene, camera);
			}

		<\/script>
`,
    };
  },
  computed: {
    classes() {
      return this.$language.isRTL(this.fieldText) ? "--rtl" : "--ltr";
    },
  },
  setup(props) {
    return useTextFieldViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.text_field_component {
  $this: &;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius-m;
  &:hover {
    #{$this}__copy-button {
      opacity: 1;
    }
  }
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $base-space;
    color: $black-87;
  }
  .content-area {
    white-space: pre-wrap;
    word-break: break-word;
  }
  &__title-content {
    word-break: break-word;
    width: calc(100% - 30px);
  }
  &__tooltip {
    display: flex;
    align-self: flex-start;
  }
  &__copy-button {
    flex-shrink: 0;
    padding: 0;
    opacity: 0;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
