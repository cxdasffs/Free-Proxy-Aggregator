<template>
  <div class="card bg-[#0a0a0a] border border-white/5 shadow-xl overflow-hidden rounded-2xl relative">
    <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50"></div>
    <div class="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
      <h3 class="font-bold text-lg tracking-wider text-gray-200 flex items-center gap-2">
        <span class="text-xl">🔌</span>
        API 提取接口
      </h3>
      <div class="badge badge-outline border-emerald-500/30 text-emerald-400 text-xs">开发者工具</div>
    </div>
    
    <div class="p-6 space-y-4">
       <!-- Controls -->
       <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Count -->
          <div>
            <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">提取数量</label>
            <input v-model.number="limit" type="number" min="1" max="5000" class="input input-sm input-bordered bg-black/50 border-white/10 w-full text-gray-300 font-mono focus:border-emerald-500" />
          </div>

          <!-- Format -->
          <div>
            <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">返回格式</label>
            <select v-model="format" class="select select-sm select-bordered bg-black/50 border-white/10 w-full text-gray-300 font-mono focus:border-emerald-500">
                <option value="text">Text (IP:Port 换行)</option>
                <option value="json">JSON (详细信息)</option>
            </select>
          </div>

          <!-- Protocol -->
          <div>
            <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">协议类型</label>
             <select v-model="protocol" class="select select-sm select-bordered bg-black/50 border-white/10 w-full text-gray-300 font-mono focus:border-emerald-500">
                <option value="all">全部</option>
                <option value="http">HTTP/HTTPS</option>
                <option value="socks">SOCKS4/5</option>
            </select>
          </div>

          <!-- Anonymity -->
          <div>
            <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">匿名度</label>
             <select v-model="anonymity" class="select select-sm select-bordered bg-black/50 border-white/10 w-full text-gray-300 font-mono focus:border-emerald-500">
                <option value="high">高匿 (Elite + Anon)</option>
                <option value="all">不限</option>
            </select>
          </div>
       </div>

       <!-- URL Display -->
       <div class="bg-black/30 border border-white/5 rounded-lg p-3 flex flex-col gap-2">
          <div class="text-[10px] text-gray-500 uppercase tracking-wider">生成的 API 链接</div>
          <div class="flex gap-2">
            <input type="text" readonly :value="apiUrl" class="input input-xs bg-transparent border-0 w-full font-mono text-emerald-400 focus:outline-none truncate" />
            <button @click="copyUrl" class="btn btn-xs btn-outline border-white/10 hover:border-emerald-500 text-gray-400 hover:text-emerald-400">
                {{ copied ? '已复制' : '复制' }}
            </button>
            <button @click="openLink" class="btn btn-xs btn-outline border-white/10 hover:border-emerald-500 text-gray-400 hover:text-emerald-400">打开</button>
          </div>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const limit = ref(100)
const format = ref('text')
const protocol = ref('all')
const anonymity = ref('high')
const copied = ref(false)

const apiUrl = computed(() => {
    // Determine base URL (use window.location.hostname for adaptability)
    const host = window.location.hostname || '127.0.0.1';
    const baseUrl = `http://${host}:8000/api/proxy/list`;
    
    const params = new URLSearchParams()
    if (limit.value !== 100) params.append('limit', limit.value)
    if (format.value !== 'json') params.append('format', format.value)
    if (protocol.value !== 'all') params.append('protocol', protocol.value)
    if (anonymity.value !== 'all') params.append('anonymity', anonymity.value)
    
    // Default country filter can be added if needed, currently kept simple
    
    const queryString = params.toString()
    return queryString ? `${baseUrl}?${queryString}` : baseUrl
})

const copyUrl = () => {
    navigator.clipboard.writeText(apiUrl.value)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
}

const openLink = () => {
    window.open(apiUrl.value, '_blank')
}
</script>
