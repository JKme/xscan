<template>
<div style="line-height:23px;font-size:15px;text-align:left; margin-left:30px">
    <el-button type="text" style="margin:0" @click="copyTarget(taskTargets)">复制扫描目标({{taskLen}})</el-button>
    <pre v-highlightjs>{{taskTargets|generatetaskTarget}}</pre>

</div>
</template>

<script>
import {
  queryTagTarget
} from '@/api/api'

export default {
  data () {
    return {
      taskTargets: [],
      taskLen: 0,
      tag_name: this.$route.params.tag_name
    }
  },
  filters: {
    format (val) {
      if (val !== undefined || val !== '') {
        return val.join('<br/>')
      }
    },

    generatetaskTarget: function (value) {
      try {
        // console.log(value.length)
        if (value !== '' && value !== undefined) {
          if (value.length > 1) { return value.join('\n') }
          return value.join('')
        }
      } catch (ex) {
        // console.log(ex)
      }
    }
  },
  methods: {
    generateLength: function (value) {
      if (value !== undefined || value !== '') {
        return value.length
      }
      return 0
    },
    queryTargets (val) {
      queryTagTarget(val).then(res => {
        this.taskTargets = res.data
        this.taskLen = this.generateLength(res.data)
        console.log(this.taskLen)
      })
    },
    copyTarget (val) {
      this.$copyText(val.join('\n'))
      this.$message.success('扫描目标已复制到剪切版')
    }

  },
  // created () {
  //   this.queryTargets({'tag_name': this.tag_name})
  // },
  mounted () {
    this.queryTargets({'tag_name': this.tag_name})
  }
}

</script>
<style>

</style>
