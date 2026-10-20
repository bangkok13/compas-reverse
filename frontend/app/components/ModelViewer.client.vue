<script setup lang="ts">
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { STLLoader } from 'three/addons/loaders/STLLoader.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
const props = defineProps<{ src: string; format: 'stl' | 'glb' }>()
const container = ref<HTMLDivElement>()
const loading = ref(true)
const error = ref('')
let renderer: THREE.WebGLRenderer | undefined
let controls: OrbitControls | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let observer: ResizeObserver | undefined
let frame = 0
let disposed = false
const abort = new AbortController()
function reset() { controls?.reset() }
function disposeObject(object: THREE.Object3D) {
  object.traverse(child => {
    const mesh = child as THREE.Mesh
    mesh.geometry?.dispose()
    const materials = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : []
    materials.forEach(material => {
      Object.values(material).forEach(value => { if (value instanceof THREE.Texture) value.dispose() })
      material.dispose()
    })
  })
}
onMounted(async () => {
  if (!container.value) return
  try {
    scene = new THREE.Scene()
    scene.background = new THREE.Color('#e7ecf2')
    camera = new THREE.PerspectiveCamera(40, 1, 0.01, 1000)
    renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2))
    container.value.appendChild(renderer.domElement)
    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    scene.add(new THREE.HemisphereLight(0xffffff, 0x40516a, 3))
    const light = new THREE.DirectionalLight(0xffffff, 4)
    light.position.set(3, 5, 4)
    scene.add(light)
    const response = await fetch(props.src, { signal: abort.signal })
    if (!response.ok) throw new Error('Model request failed')
    const buffer = await response.arrayBuffer()
    let model: THREE.Object3D
    if (props.format === 'stl') {
      const geometry = new STLLoader().parse(buffer)
      geometry.computeVertexNormals()
      model = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color: '#437ed1', roughness: 0.45, metalness: 0.3 }))
    } else {
      const manager = new THREE.LoadingManager()
      // A GLB must be self-contained. Block external texture/buffer requests.
      manager.setURLModifier(url => {
        if (url.startsWith('blob:') || url.startsWith('data:')) return url
        throw new Error('External model resources are not allowed')
      })
      model = (await new GLTFLoader(manager).parseAsync(buffer, '')).scene
    }
    if (disposed) { disposeObject(model); return }
    const box = new THREE.Box3().setFromObject(model)
    const size = box.getSize(new THREE.Vector3()).length()
    if (!Number.isFinite(size) || size <= 0) { disposeObject(model); throw new Error('Empty geometry') }
    model.position.sub(box.getCenter(new THREE.Vector3()))
    const group = new THREE.Group()
    group.add(model)
    group.scale.setScalar(3 / size)
    scene.add(group)
    camera.position.set(4, 3, 5)
    controls.saveState()
    const resize = () => {
      if (!container.value || !renderer || !camera) return
      const width = container.value.clientWidth
      renderer.setSize(width, 440)
      camera.aspect = width / 440
      camera.updateProjectionMatrix()
    }
    observer = new ResizeObserver(resize)
    observer.observe(container.value)
    resize()
    const render = () => {
      if (disposed) return
      controls?.update()
      renderer?.render(scene!, camera!)
      frame = requestAnimationFrame(render)
    }
    render()
  } catch {
    if (!disposed) error.value = 'Модель не удалось открыть. Проверьте поддержку WebGL или попробуйте другой браузер.'
  } finally { loading.value = false }
})
onBeforeUnmount(() => {
  disposed = true
  abort.abort()
  cancelAnimationFrame(frame)
  observer?.disconnect()
  controls?.dispose()
  if (scene) disposeObject(scene)
  renderer?.dispose()
})
</script>
<template><div class="viewer"><div ref="container" class="viewer-canvas" aria-label="3D-модель: перетаскивайте для вращения, используйте колесо для масштаба" /><p v-if="loading" role="status">Загружаем модель…</p><p v-else-if="error" role="alert">{{ error }}</p><div v-else class="viewer-footer"><span>Перетаскивайте для вращения · Прокрутка для масштаба</span><button @click="reset">Сбросить вид ↺</button></div></div></template>
