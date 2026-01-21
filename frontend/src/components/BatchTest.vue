<template>
  <div class="card bg-[#0a0a0a] border border-white/5 shadow-xl overflow-hidden rounded-2xl relative">
    <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50"></div>
    <div class="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
      <h3 class="font-bold text-lg tracking-wider text-gray-200 flex items-center gap-2">
        <span class="text-xl">🧪</span>
        批量测试工具
      </h3>
      <div class="badge badge-outline border-purple-500/30 text-purple-400 text-xs">实验性</div>
    </div>
    <div class="p-6 space-y-4">
       <!-- Test Controls -->
       <div class="flex flex-wrap gap-4">
          <div class="flex-1 min-w-[200px]">
              <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">选择国家/地区</label>
              <select v-model="batchTestCountry" class="select select-bordered bg-black/50 border-white/10 w-full focus:border-purple-500 focus:outline-none text-sm font-mono text-gray-300">
                  <option value="all">全部国家</option>
                  <option value="CN">🇨🇳 中国 (CN)</option>
                  <option value="US">🇺🇸 美国 (US)</option>
                  <option value="FR">🇫🇷 法国 (FR)</option>
                  <option value="SG">🇸🇬 新加坡 (SG)</option>
                  <option value="ID">🇮🇩 印尼 (ID)</option>
                  <option value="NL">🇳🇱 荷兰 (NL)</option>
                  <option value="DE">🇩🇪 德国 (DE)</option>
                  <option value="JP">🇯🇵 日本 (JP)</option>
                  <option value="KR">🇰🇷 韩国 (KR)</option>
              </select>
          </div>
          <div class="w-32">
              <label class="label text-xs font-bold text-gray-500 uppercase tracking-widest">测试数量</label>
              <input v-model.number="batchTestCount" type="number" min="5" max="50" class="input input-bordered bg-black/50 border-white/10 w-full focus:border-purple-500 focus:outline-none text-sm font-mono text-gray-300" />
          </div>
          <div class="flex items-end">
              <button class="btn btn-outline border-purple-500/30 text-purple-400 hover:bg-purple-500/10 hover:border-purple-400 hover:text-purple-300 uppercase tracking-widest text-xs" 
                      @click="runBatchTest" :disabled="batchTesting">
                  <span v-if="batchTesting" class="loading loading-spinner loading-xs"></span>
                  {{ batchTesting ? '测试中...' : '开始批量测试' }}
              </button>
          </div>
       </div>

       <!-- Test Results -->
       <div v-if="batchTestResults" class="mt-6">
          <!-- Summary -->
          <div class="grid grid-cols-3 gap-4 mb-4">
              <div class="bg-black/30 border border-white/5 rounded-lg p-4">
                  <div class="text-xs text-gray-500 uppercase tracking-wider">测试总数</div>
                  <div class="text-2xl font-bold text-white mt-1">{{ batchTestResults.total_tested }}</div>
              </div>
              <div class="bg-black/30 border border-white/5 rounded-lg p-4">
                  <div class="text-xs text-gray-500 uppercase tracking-wider">通过数量</div>
                  <div class="text-2xl font-bold text-emerald-500 mt-1">{{ batchTestResults.total_passed }}</div>
              </div>
              <div class="bg-black/30 border border-white/5 rounded-lg p-4">
                  <div class="text-xs text-gray-500 uppercase tracking-wider">成功率</div>
                  <div class="text-2xl font-bold text-cyan-500 mt-1">{{ batchTestResults.success_rate }}</div>
              </div>
          </div>

          <!-- Results Table -->
          <div class="overflow-x-auto max-h-96 overflow-y-auto custom-scrollbar">
              <table class="table table-xs w-full">
                  <thead class="sticky top-0 bg-[#0a0a0a] z-10">
                      <tr class="border-b border-white/10">
                          <th class="text-gray-400 font-bold uppercase text-xs">代理</th>
                          <th class="text-gray-400 font-bold uppercase text-xs">国家</th>
                          <th class="text-gray-400 font-bold uppercase text-xs">协议</th>
                          <th class="text-gray-400 font-bold uppercase text-xs">来源</th>
                          <th class="text-gray-400 font-bold uppercase text-xs">状态</th>
                          <th class="text-gray-400 font-bold uppercase text-xs">延迟</th>
                          <th class="text-gray-400 font-bold uppercase text-xs">评分</th>
                      </tr>
                  </thead>
                  <tbody>
                      <tr v-for="(result, index) in batchTestResults.results" :key="index" 
                          class="border-b border-white/5 hover:bg-white/5 transition-colors"
                          :class="result.success ? 'bg-emerald-900/10' : 'bg-red-900/10'">
                          <td class="font-mono text-xs text-gray-300">{{ result.proxy }}</td>
                          <td class="text-xs">
                              <span class="badge badge-xs badge-outline border-white/20 text-gray-400">{{ result.country }}</span>
                          </td>
                          <td class="text-xs">
                              <span class="badge badge-xs bg-cyan-900/20 text-cyan-400 border-0">{{ result.protocol }}</span>
                          </td>
                          <td class="text-xs text-gray-500">{{ result.source }}</td>
                          <td class="text-xs">
                              <span v-if="result.success" class="text-emerald-500 font-bold">✓ 成功</span>
                              <span v-else class="text-red-500 font-bold">✗ 失败</span>
                          </td>
                          <td class="font-mono text-xs" :class="result.success ? 'text-emerald-400' : 'text-gray-600'">
                              {{ result.latency_ms }}ms
                          </td>
                          <td>
                              <div class="radial-progress text-[9px] font-bold" 
                                   :class="getScoreColor(result.score)" 
                                   :style="`--value:${result.score}; --size:1.5rem;`">
                                {{ result.score }}
                              </div>
                          </td>
                      </tr>
                  </tbody>
              </table>
          </div>
       </div>

       <!-- Empty State -->
       <div v-if="!batchTestResults && !batchTesting" class="text-center py-12 text-gray-600 italic">
          选择国家/地区和测试数量，然后点击"开始批量测试"
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const batchTestCountry = ref('all')
const batchTestCount = ref(10)
const batchTesting = ref(false)
const batchTestResults = ref(null)

const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-red-500';
}

const runBatchTest = async () => {
    batchTesting.value = true
    batchTestResults.value = null
    
    try {
        const res = await axios.post('http://127.0.0.1:8000/api/proxy/batch-test', {
            country: batchTestCountry.value,
            count: batchTestCount.value,
            test_url: 'http://www.baidu.com'
        })
        batchTestResults.value = res.data
    } catch (e) {
        console.error("Batch test error:", e)
        alert('批量测试失败: ' + e.message)
    } finally {
        batchTesting.value = false
    }
}
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
</style>
