<template>
  <div ref="chart" style="width: 100%; height: 100%; min-height: 400px;"></div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps(['data']);
const chart = ref(null);
let myChart = null;

// Manual mapping from ISO 2-letter code to ECharts Map Name
const countryNameMap = {
    'US': 'United States',
    'CN': 'China',
    'RU': 'Russia',
    'DE': 'Germany',
    'UK': 'United Kingdom',
    'GB': 'United Kingdom',
    'FR': 'France',
    'BR': 'Brazil',
    'CA': 'Canada',
    'IN': 'India',
    'JP': 'Japan',
    'AU': 'Australia',
    'IT': 'Italy',
    'ZA': 'South Africa',
    'KR': 'South Korea',
    'MX': 'Mexico',
    'SG': 'Singapore',
    'HK': 'Hong Kong',
    'TW': 'Taiwan',
    'NL': 'Netherlands',
    'BD': 'Bangladesh',
    'KH': 'Cambodia',
    'LA': 'Laos',
    'PH': 'Philippines',
    'ID': 'Indonesia',
    'VN': 'Vietnam',
    'TH': 'Thailand',
    'RO': 'Romania',
    'PL': 'Poland',
    'ES': 'Spain',
    'CH': 'Switzerland',
    'AT': 'Austria',
    'SE': 'Sweden',
    'NO': 'Norway',
    'FI': 'Finland',
    'DK': 'Denmark',
    'BE': 'Belgium',
    'CZ': 'Czech Republic',
    'SK': 'Slovakia',
    'HU': 'Hungary',
    'LV': 'Latvia',
    'EE': 'Estonia',
    'LT': 'Lithuania',
    'AR': 'Argentina',
    'CL': 'Chile',
    'KZ': 'Kazakhstan',
    'BA': 'Bosnia and Herzegovina',
    'SN': 'Senegal',
    'RW': 'Rwanda',
    'KE': 'Kenya',
    'LY': 'Libya',
    'GH': 'Ghana',
    'SC': 'Seychelles',
    'EG': 'Egypt',
    'NG': 'Nigeria',
    'TR': 'Turkey',
    'SA': 'Saudi Arabia',
    'AE': 'United Arab Emirates',
    'IL': 'Israel',
    'IQ': 'Iraq',
    'IR': 'Iran',
    'PK': 'Pakistan',
    'MY': 'Malaysia',
    'NZ': 'New Zealand',
    'AM': 'Armenia',
    'CO': 'Colombia',
    'PE': 'Peru',
    'EC': 'Ecuador',
    'DO': 'Dominican Republic',
    'VE': 'Venezuela',
    'PR': 'Puerto Rico',
    'YE': 'Yemen',
    'UA': 'Ukraine',
    'MN': 'Mongolia',
    'LU': 'Luxembourg',
    'LS': 'Lesotho',
    'LB': 'Lebanon',
    'IE': 'Ireland',
    'HR': 'Croatia',
    'HN': 'Honduras',
    'GY': 'Guyana',
    'GR': 'Greece',
    'AL': 'Albania',
};

const mapCountryName = (code) => {
    if (code === 'Unknown' || code === 'ZZ') return null; // Don't show on map
    return countryNameMap[code] || code;
}

const initChart = () => {
  if (!chart.value) return;
  myChart = echarts.init(chart.value);
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: '#06b6d4',
      textStyle: {
        color: '#fff'
      }
    },
    visualMap: {
      min: 0,
      max: 100,
      left: 'left',
      top: 'bottom',
      text: ['高', '低'],
      calculable: true,
      inRange: {
        color: ['#0f172a', '#06b6d4'] // Dark slate to Cyan
      },
      textStyle: {
        color: '#94a3b8'
      }
    },
    geo: {
      map: 'world',
      roam: true,
      zoom: 1.2,
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: false
        },
        itemStyle: {
          areaColor: '#0e7490' // cyan-700
        }
      },
      itemStyle: {
        areaColor: '#1e293b', // slate-800
        borderColor: '#334155', // slate-700
        borderWidth: 1
      }
    },
    series: [
      {
        type: 'map',
        map: 'world',
        geoIndex: 0,
        data: [] 
      }
    ]
  };
  myChart.setOption(option);
};

const loadMap = async () => {
    try {
        const response = await fetch('https://raw.githubusercontent.com/apache/echarts-examples/gh-pages/public/data/asset/geo/world.json');
        const mapJson = await response.json();
        echarts.registerMap('world', mapJson);
        
        // Now initialize the chart AFTER map is registered
        initChart();
        
        // Update with data if available
        if (props.data && myChart) {
             myChart.setOption({
                series: [{
                    data: props.data.map(d => ({ name: mapCountryName(d.country), value: d.count }))
                }]
            });
        }
    } catch (e) {
        console.error("Failed to load map", e);
        // Fallback: show empty chart
        if (chart.value && !myChart) {
            myChart = echarts.init(chart.value);
            myChart.setOption({
                title: {
                    text: '地图加载失败',
                    left: 'center',
                    top: 'center',
                    textStyle: { color: '#666' }
                }
            });
        }
    }
}

const resizeChart = () => {
  myChart && myChart.resize();
};

onMounted(() => {
  // Load map first, THEN init chart
  loadMap();
  window.addEventListener('resize', resizeChart);
});

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart);
  myChart && myChart.dispose();
});

watch(() => props.data, (newData) => {
    if (myChart && newData) {
        myChart.setOption({
            series: [{
                data: newData.map(d => ({ name: mapCountryName(d.country), value: d.count || d.value }))
            }]
        });
    }
});
</script>
