<template>
  <div class="min-h-screen bg-[#050505] text-gray-200 font-mono selection:bg-cyan-500 selection:text-black" data-theme="black">
    
    <!-- Cyberpunk Background Grid -->
    <div class="fixed inset-0 z-0 pointer-events-none opacity-20" 
         style="background-image: linear-gradient(#1a1a1a 1px, transparent 1px), linear-gradient(90deg, #1a1a1a 1px, transparent 1px); background-size: 30px 30px;">
    </div>

    <!-- Main Container -->
    <div class="relative z-10 container mx-auto p-6 lg:p-10 max-w-[1920px]">
      
      <!-- Navbar -->
      <nav class="navbar bg-[#0a0a0a]/80 backdrop-blur-md border-b border-white/5 rounded-2xl mb-10 sticky top-4 z-50 shadow-[0_0_20px_rgba(0,0,0,0.5)]">
        <div class="flex-1">
          <a class="btn btn-ghost normal-case text-2xl gap-3 hover:bg-transparent">
            <span class="text-4xl">🕷️</span>
            <div class="flex flex-col items-start leading-none">
              <span class="font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 tracking-wider">军火库</span>
              <span class="text-[10px] text-gray-500 uppercase tracking-[0.2em]">代理池架构</span>
            </div>
          </a>
        </div>
        <div class="flex-none gap-4">
          <div class="flex items-center gap-2 px-4 py-2 rounded-full border border-white/5 bg-black/50">
            <div class="w-2 h-2 rounded-full animate-pulse" :class="connected ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-red-500 shadow-[0_0_10px_#ef4444]'"></div>
            <span class="text-xs font-bold tracking-wider" :class="connected ? 'text-emerald-500' : 'text-red-500'">
              {{ connected ? '系统在线' : '已断开连接' }}
            </span>
          </div>
          <button class="btn btn-sm btn-outline border-purple-500/30 text-purple-400 hover:bg-purple-500/10 hover:border-purple-400 hover:text-purple-300 transition-all duration-300 uppercase tracking-widest text-xs" 
                  @click="triggerCrawl" :disabled="crawling">
            <span v-if="crawling" class="loading loading-spinner loading-xs"></span>
            {{ crawling ? '正在扫描...' : '开始扫描' }}
          </button>
          <button class="btn btn-sm btn-outline border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-400 hover:text-cyan-300 transition-all duration-300 uppercase tracking-widest text-xs" 
                  @click="fetchData" :disabled="loading">
            <span v-if="loading" class="loading loading-spinner loading-xs"></span>
            {{ loading ? '同步中...' : '刷新数据' }}
          </button>
        </div>
      </nav>

      <!-- Stats Row -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="stat relative overflow-hidden bg-[#0a0a0a] border border-white/5 rounded-2xl group hover:border-cyan-500/30 transition-colors">
          <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="stat-figure text-cyan-500/20 group-hover:text-cyan-500/40 transition-colors duration-500">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-16 h-16 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
          </div>
          <div class="stat-title text-gray-500 text-xs font-bold tracking-widest uppercase">活跃节点</div>
          <div class="stat-value text-4xl lg:text-5xl font-black text-white mt-2 font-sans tracking-tight">
            {{ formatNumber(stats.total_active || 0) }}
          </div>
          <div class="stat-desc text-cyan-500 font-bold mt-2 flex items-center gap-1">
            <span>●</span> 实时代理
          </div>
        </div>

        <div class="stat relative overflow-hidden bg-[#0a0a0a] border border-white/5 rounded-2xl group hover:border-emerald-500/30 transition-colors">
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="stat-figure text-emerald-500/20 group-hover:text-emerald-500/40 transition-colors duration-500">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-16 h-16 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          </div>
          <div class="stat-title text-gray-500 text-xs font-bold tracking-widest uppercase">网络延迟</div>
          <div class="stat-value text-4xl lg:text-5xl font-black text-white mt-2 font-sans tracking-tight">
            {{ stats.avg_speed || 0 }}<span class="text-2xl text-gray-600 font-normal ml-1">ms</span>
          </div>
          <div class="stat-desc text-emerald-500 font-bold mt-2">全球平均</div>
        </div>

        <div class="stat relative overflow-hidden bg-[#0a0a0a] border border-white/5 rounded-2xl group hover:border-purple-500/30 transition-colors">
          <div class="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div class="stat-figure text-purple-500/20 group-hover:text-purple-500/40 transition-colors duration-500">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-16 h-16 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <div class="stat-title text-gray-500 text-xs font-bold tracking-widest uppercase">系统完整性</div>
          <div class="stat-value text-4xl lg:text-5xl font-black text-white mt-2 font-sans tracking-tight">
            100<span class="text-2xl text-gray-600 font-normal ml-1">%</span>
          </div>
          <div class="stat-desc text-purple-500 font-bold mt-2">性能最佳</div>
        </div>
      </div>

      <!-- Main 4-Grid Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <!-- Top Left: Map -->
        <div class="card bg-[#0a0a0a] border border-white/5 shadow-xl overflow-hidden rounded-2xl relative">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50"></div>
          <div class="p-6 border-b border-white/5 flex justify-between items-center">
            <h3 class="font-bold text-lg tracking-wider text-gray-200 flex items-center gap-2">
              <span class="w-2 h-2 bg-cyan-500 rounded-full"></span>
              空间情报概览
            </h3>
            <div class="badge badge-outline border-white/10 text-gray-500 text-xs">实时</div>
          </div>
          <div class="bg-[#050505] relative">
             <ProxyMap :data="stats.country_distribution || []" />
             <div class="absolute inset-0 pointer-events-none opacity-5 bg-[linear-gradient(transparent_50%,black_50%)] bg-[length:100%_4px]"></div>
          </div>
        </div>

        <!-- Top Right: Attack Dashboard -->
        <div class="card bg-[#0a0a0a] border border-white/5 shadow-xl overflow-hidden rounded-2xl relative">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-red-500 to-transparent opacity-50"></div>
          <div class="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
            <h3 class="font-bold text-lg tracking-wider text-gray-200 flex items-center gap-2">
              <span class="text-xl">🎯</span>
              目标靶场
            </h3>
            <div class="badge badge-outline border-red-500/30 text-red-400 text-xs">渗透测试</div>
          </div>
          <div class="p-6 space-y-4">
             <!-- Attack Controls -->
             <div class="space-y-3">
                <div>
                    <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">目标 URL</label>
                    <input v-model="testUrl" type="text" placeholder="https://example.com" class="input input-bordered bg-black/50 border-white/10 w-full focus:border-red-500 focus:outline-none text-sm font-mono text-red-500" />
                </div>
                <div class="grid grid-cols-4 gap-2">
                    <div>
                        <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">区域</label>
                        <select v-model="testRegion" class="select select-bordered bg-black/50 border-white/10 w-full focus:border-red-500 focus:outline-none text-xs font-mono text-gray-300 px-2">
                            <option value="all">全球</option>
                            <option value="domestic">CN</option>
                            <option value="foreign">海外</option>
                        </select>
                    </div>
                    <div>
                        <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">协议</label>
                        <select v-model="testProtocol" class="select select-bordered bg-black/50 border-white/10 w-full focus:border-red-500 focus:outline-none text-xs font-mono text-gray-300 px-2">
                            <option value="all">ALL</option>
                            <option value="http">HTTP</option>
                            <option value="socks">SOCKS</option>
                        </select>
                    </div>
                    <div>
                        <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">排序</label>
                        <select v-model="testSortBy" class="select select-bordered bg-black/50 border-white/10 w-full focus:border-red-500 focus:outline-none text-xs font-mono text-gray-300 px-2">
                            <option value="score">综合</option>
                            <option value="speed">极速</option>
                        </select>
                    </div>
                    <div>
                        <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">
                            数量 
                            <span class="text-[10px] text-red-500 cursor-pointer hover:underline ml-1" @click="attackCount = 99999">ALL</span>
                        </label>
                        <input v-model.number="attackCount" type="number" min="1" max="100000" class="input input-bordered bg-black/50 border-white/10 w-full focus:border-red-500 focus:outline-none text-xs font-mono text-gray-300 px-2" />
                    </div>
                </div>
                <!-- Mode Indicator -->
                <div class="text-[10px] text-gray-500 text-center -mt-1">
                    <span v-if="testSpecificIp">🎯 锁定模式</span>
                    <span v-else-if="attackCount >= 10000">🛡️ 严格模式：只使用已验证的高匿代理 (Elite)</span>
                    <span v-else>🤖 智能模式：优先使用高分代理</span>
                </div>
                <div class="flex items-center space-x-2 my-2">
                     <div class="flex-1">
                         <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">指定攻击IP (可选)</label>
                         <input v-model="testSpecificIp" type="text" placeholder="IP:Port (留空自动)" class="input input-bordered bg-black/50 border-white/10 w-full focus:border-red-500 focus:outline-none text-xs font-mono text-blue-400 px-2 h-8" />
                     </div>
                     <div class="form-control">
                        <label class="label cursor-pointer flex flex-col items-center">
                          <span class="label-text text-[10px] text-red-500 font-bold mb-1">取消严选</span> 
                          <input type="checkbox" v-model="allowUnsafe" @change="handleUnsafeChange" class="checkbox checkbox-xs checkbox-error" />
                        </label>
                      </div>
                </div>
                <button class="btn btn-outline border-red-500/30 text-red-400 w-full hover:bg-red-500/10 hover:border-red-400 hover:text-red-300 uppercase tracking-widest text-xs" 
                        @click="runTest" :disabled="testing">
                    <span v-if="testing" class="loading loading-spinner loading-xs"></span>
                    {{ testing ? '渗透中...' : '发起攻击测试' }}
                </button>
             </div>

             <!-- Real-time Attack Stats -->
             <div v-if="testResult" class="space-y-3">
                <div class="grid grid-cols-4 gap-2">
                    <div class="bg-black/30 border border-white/5 rounded p-3 text-center">
                        <div class="text-[10px] text-gray-500 uppercase">攻击</div>
                        <div class="text-2xl font-bold text-white">{{ testResult.attack_count }}</div>
                    </div>
                    <div class="bg-black/30 border border-emerald-500/20 rounded p-3 text-center">
                        <div class="text-[10px] text-gray-500 uppercase">成功</div>
                        <div class="text-2xl font-bold text-emerald-500">{{ testResult.success_count }}</div>
                    </div>
                    <div class="bg-black/30 border border-red-500/20 rounded p-3 text-center">
                        <div class="text-[10px] text-gray-500 uppercase">失败</div>
                        <div class="text-2xl font-bold text-red-500">{{ testResult.failure_count }}</div>
                    </div>
                    <div class="bg-black/30 border border-cyan-500/20 rounded p-3 text-center">
                        <div class="text-[10px] text-gray-500 uppercase">成功率</div>
                        <div class="text-xl font-bold text-cyan-500">{{ testResult.success_rate }}</div>
                    </div>
                </div>

                <!-- Real-time Results Stream -->
                <div class="bg-black/30 border border-white/5 rounded-lg p-4 max-h-[400px] overflow-y-auto custom-scrollbar">
                    <div class="space-y-2">
                        <div v-for="(result, index) in testResult.results" :key="index" 
                             class="flex items-center justify-between p-2 rounded border"
                             :class="result.success ? 'border-emerald-500/30 bg-emerald-900/10' : 'border-red-500/30 bg-red-900/10'">
                            <div class="flex items-center gap-2">
                                <span v-if="result.success" class="text-emerald-500 text-lg">✓</span>
                                <span v-else class="text-red-500 text-lg">✗</span>
                                <div>
                                    <div class="font-mono text-xs text-gray-300">{{ result.proxy }}</div>
                                    <div class="text-[10px] text-gray-500">
                                        {{ result.country }} · {{ result.protocol }}
                                        <span v-if="result.error" class="text-red-400 ml-2">{{ result.error }}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="font-mono text-sm" :class="result.success ? 'text-emerald-400' : 'text-gray-600'">
                                    {{ result.time_ms }}ms
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
             </div>
          </div>
        </div>

        <!-- Bottom Left: Batch Test Tool -->
        <!-- Bottom Left: API Extractor -->
        <ApiExtractor />

        <!-- Bottom Right: Regional IP Rankings -->
        <div class="card bg-[#0a0a0a] border border-white/5 shadow-xl overflow-hidden rounded-2xl relative">
          <div class="p-6 border-b border-white/5 bg-white/[0.02] flex flex-col gap-4">
            <div class="flex items-center justify-between">
              <h3 class="font-bold text-gray-200 tracking-wider flex items-center justify-between">
                <span>🌍 各地区热门IP排行</span>
              </h3>
            </div>
            <!-- Filters -->
            <div class="flex flex-wrap gap-2">
                <select v-model="filterSource" @change="fetchData" class="select select-xs select-bordered bg-black/50 border-white/10 text-xs text-gray-300 focus:border-cyan-500">
                    <option value="all">所有来源</option>
                    <option value="proxifly">Proxifly</option>
                    <option value="89ip">89ip (国内)</option>
                    <option value="ip3366">ip3366 (云代理)</option>
                </select>
                <select v-model="filterRegion" @change="fetchData" class="select select-xs select-bordered bg-black/50 border-white/10 text-xs text-gray-300 focus:border-cyan-500">
                    <option value="all">全球区域</option>
                    <option value="domestic">仅限国内 (CN)</option>
                    <option value="foreign">仅限海外</option>
                </select>
            </div>
          </div>
        
        <div class="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2 max-h-[600px]">
           <div v-if="proxies.length === 0" class="text-center py-20 text-gray-600 italic">
             正在扫描频段... 无信号.
           </div>
          
          <div v-for="item in proxies" :key="item.id" 
               class="group flex items-center justify-between p-3 rounded-lg border border-transparent hover:border-white/10 hover:bg-white/5 transition-all cursor-default">
             <!-- IP Info -->
             <div class="flex flex-col">
               <div class="flex items-center gap-2">
                 <span class="text-[10px] font-bold text-gray-400 border border-white/10 px-1 rounded uppercase">{{ item.source || 'UNK' }}</span>
                 <span class="text-xs font-bold text-cyan-400 font-mono bg-cyan-900/20 px-1.5 py-0.5 rounded">{{ item.protocol.toUpperCase() }}</span>
                 <span class="text-sm font-bold text-gray-300 font-mono">{{ item.ip }}</span>
               </div>
               <div class="flex items-center gap-2 mt-1">
                  <span class="text-[10px] text-gray-500 uppercase tracking-wider flex items-center gap-1">
                    <span class="w-3 h-2 block bg-white/10 rounded-sm overflow-hidden relative">
                       <div class="absolute inset-0 bg-gray-600"></div>
                    </span>
                    {{ item.country }}
                  </span>
                  <span class="text-[10px] text-gray-600 font-mono">::{{ item.port }}</span>
               </div>
             </div>

             <!-- Score Radial -->
             <div class="flex flex-col items-end gap-1">
                <div class="radial-progress text-[10px] font-bold" 
                     :class="getScoreColor(item.score)" 
                     :style="`--value:${item.score}; --size:2rem;`" role="progressbar">
                  {{ item.score }}
                </div>
                <span class="text-[9px] font-mono opacity-50" :class="getScoreTextColor(item.score)">MS: {{ item.speed }}</span>
             </div>
          </div>
        </div>
      </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ProxyMap from './components/ProxyMap.vue'
import ApiExtractor from './components/ApiExtractor.vue'
import axios from 'axios'

const proxies = ref([])
const stats = ref({})
const loading = ref(false)
const crawling = ref(false)
const connected = ref(false)
const filterSource = ref('all')
const filterRegion = ref('all')

// Test Module
// Test Module
const testUrl = ref('')
const testRegion = ref('all')
const testProtocol = ref('all')
const testSpecificIp = ref('')
const testSortBy = ref('score')
const allowUnsafe = ref(false)
const attackCount = ref(5)
const testing = ref(false)
const testResult = ref(null)

const handleUnsafeChange = () => {
    if (allowUnsafe.value) {
        if (!confirm("⚠️ 警告：取消高匿限制 (Unsafe Mode)\n\n取消后，系统将使用大量 '未知匿名度' 的代理。这可能会：\n1. 导致您的真实IP泄露（如果遇到透明代理）。\n2. 代理质量参差不齐，失败率飙升。\n\n您确定要为了追求数量而牺牲安全性吗？")) {
             allowUnsafe.value = false;
        }
    }
}

const runTest = () => {
    if (!testUrl.value) return;
    
    // Close existing connection if any
    if (testing.value && window.currentEventSource) {
        window.currentEventSource.close();
        testing.value = false;
        return;
    }
    
    // Reset stats
    // Note: The instruction `testResult.value = []` would cause runtime errors
    // as `testResult` is expected to be an object with properties like `attack_count`.
    // Keeping the original object structure and resetting its properties.
    testResult.value = {
        attack_count: 0,
        success_count: 0,
        failure_count: 0,
        success_rate: '0%',
        results: []
    }
    testing.value = true
    
    // Construct URL
    // Use absolute URL to avoid 404 on Vite dev server
    let url = `http://127.0.0.1:8000/api/proxy/attack-stream?url=${encodeURIComponent(testUrl.value)}&attack_count=${attackCount.value}&region=${testRegion.value}&protocol=${testProtocol.value}&sort_by=${testSortBy.value}&allow_unsafe=${allowUnsafe.value}`;
    if (testSpecificIp.value.trim()) {
        url += `&specific_ip=${encodeURIComponent(testSpecificIp.value.trim())}`;
    }
    
    const evtSource = new EventSource(url);
    window.currentEventSource = evtSource;
    
    evtSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'start') {
            testResult.value.attack_count = data.total;
        } else if (data.type === 'result') {
            testResult.value.results.unshift(data); // Add to top
            
            if (data.success) {
                testResult.value.success_count++;
            } else {
                testResult.value.failure_count++;
            }
            
            // Recalculate rate
            const total = testResult.value.success_count + testResult.value.failure_count;
            if (total > 0) {
                testResult.value.success_rate = ((testResult.value.success_count / total) * 100).toFixed(1) + '%';
            }
        } else if (data.type === 'end') {
            evtSource.close();
            testing.value = false;
        }
    };
    
    evtSource.onerror = (err) => {
        console.error("SSE Error:", err);
        evtSource.close();
        testing.value = false;
    };
}

const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-red-500';
}

const getScoreTextColor = (score) => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
}

const fetchData = async () => {
  loading.value = true
  try {
    const listRes = await axios.get('http://127.0.0.1:8000/api/proxy/list', {
        params: {
            source: filterSource.value,
            region: filterRegion.value
        }
    })
    proxies.value = listRes.data

    const statsRes = await axios.get('http://127.0.0.1:8000/api/proxy/stats')
    stats.value = statsRes.data
    
    connected.value = true
  } catch (error) {
    console.error("Backend Error:", error)
    connected.value = false
  } finally {
    loading.value = false
  }
}

const triggerCrawl = async () => {
  crawling.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/proxy/crawl')
    setTimeout(() => {
        fetchData()
    }, 2000)
  } catch (error) {
    console.error("Crawl Trigger Error:", error)
  } finally {
    setTimeout(() => {
        crawling.value = false
    }, 1000)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>