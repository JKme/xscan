<template>
<div>
           <div class="breadcrumb" v-if="$route.path!=='/'">
            <el-breadcrumb separator-class="el-icon-arrow-right">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item :to="{ path: '/' }">任务管理</el-breadcrumb-item>
                <el-breadcrumb-item>{{$route.params.task_id}}</el-breadcrumb-item>
            </el-breadcrumb>
    </div>
    <el-tabs
            v-model="activeName"
            type="border-card"
            lazy
            @tab-click="handleTabClick"
            :active-name="activeName">
        <el-tab-pane name="vuln">
            <span slot="label"><i class="iconfont icon-search"></i>发现的漏洞 <span :style="{'color': colorChange(vulCount)}">({{vulCount}})</span></span>
            <Vuln :on-value-change='getVulCount'></Vuln>
        </el-tab-pane>
        <el-tab-pane name="bbscan">
            <span slot="label"><i class="iconfont icon-shielding"></i>目录爬虫 <span :style="{'color': colorChange(SpiderCount)}">({{SpiderCount}})</span></span>
            <BBScan :task-id="task_id" :active-tab="activeName" :on-value-change='getSpiderCount'></BBScan>
        </el-tab-pane>
        <el-tab-pane name="devices">
            <span slot="label"><i class="iconfont icon-alert"></i>开放的端口 <span :style="{'color': colorChange(deviceCount)}">({{deviceCount}})</span></span>
            <Device :on-value-change='getDeviceCount'></Device>
        </el-tab-pane>
        <!-- <el-tab-pane name="return">
          <span slot="label">
          <router-link style="color: rgb(77, 85, 93);text-decoration: none;" :to="{name: 'tasks', params: {'path': '/'}}">
          返回首页</router-link></span>
        </el-tab-pane> -->
        <!-- <el-tab-pane name="task">
            <span slot="label"><i class="iconfont icon-task"></i>定时任务</span>
            <Task></Task>
        </el-tab-pane>
        <el-tab-pane name="github">
            <span slot="label"><i class="iconfont icon-github-fill"></i>GitHub账号</span>
            <Github></Github>
        </el-tab-pane> -->
    </el-tabs>
</div>
</template>
<script>
const Vuln = () => import('./plugins/Vuln')
const BBScan = () => import('./plugins/BBscan')
const Device = () => import('./plugins/Device')
export default {
  data () {
    return {
      vulCount: 0,
      SpiderCount: 0,
      deviceCount: 0,
      activeName: this.$route.params.tab ? this.$route.params.tab : 'vuln',
      task_id: this.$route.params.task_id
    }
  },
  components: {
    Vuln,
    BBScan,
    Device
  },
  methods: {
    handleTabClick (tab) {
      this.task_id = this.$route.params.task_id
    //   console.log(tab.name)
    //   console.log(this.$route.params.task_id)
    //   this.$router.push({name: 'taskDetail', params: {tab: tab.name}})
    },
    getVulCount (value) {
      this.vulCount = value
    },
    getSpiderCount (value) {
      this.SpiderCount = value
    },
    getDeviceCount (value) {
      this.deviceCount = value
    },
    colorChange (value) {
      let color = ''
      if (value !== undefined && value > 0 && value !== '') {
        color = '#ff0000'
      } else {
        color = '#409eff'
      }
      return color
    }
  },
  mounted () {
    // task_id = this.$route.params.task_id
  }
}
</script>>

<style>
    .el-tabs__nav-next, .el-tabs__nav-prev {
        margin-left: 5px;
        margin-right: 5px;
    }

    .tip a {
        text-decoration: none;
        line-height: 36px;
        color: #409eff;
    }

    .el-tab-pane {
        padding: 20px 5px 10px 5px;
    }

    .el-tabs--border-card {
        background: #fff;
        border: 1px solid #ebeef5;
        border-radius: 4px;
        -webkit-box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.12),
        0 0 6px 0 rgba(0, 0, 0, 0.04);
        box-shadow: none !important;
    }

    .el-tabs__nav i {
        margin-right: 5px;
    }
</style>
