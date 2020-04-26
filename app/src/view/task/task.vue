<template>
<div class='main-div-container'>
<el-form :model="ruleForm" :rules="rules" ref="ruleForm" label-width="90px" class="demo-ruleForm">
  <el-form-item label="任务名称:"  prop="name">
    <el-input v-model="ruleForm.name"></el-input>
  </el-form-item>
  <el-form-item label="扫描目标:" prop="target">
    <el-input type="textarea" placeholder="请输入IP或者域名" v-model="ruleForm.target"></el-input>
  </el-form-item>
  <el-form-item label="目标分类:"  prop="tag_name" >
    <el-select v-model="ruleForm.tag_name"  clearable placeholder="请选择分类">
      <el-option
        v-for="tag in tags"
        :key="tag.value"
        :label="tag.label"
        :value="tag.value">
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item label="目录爬虫:" prop="BBScan">
    <el-switch v-model="ruleForm.BBScan"></el-switch>
  </el-form-item>
  <el-form-item label="端口扫描:" prop="port">
    <el-input v-model="ruleForm.port" clearable placeholder="1-65535"></el-input>
  </el-form-item>
  <el-form-item label="漏洞扫描:" v-model="ruleForm.poc" prop="poc" >
   <pocOption @pocSelect='pocSelect' ref="PocOptionItemForm"></pocOption>
  </el-form-item>

    <!-- <el-form-item label="漏洞扫描:" v-model="ruleForm.poc" prop="poc" >
   <pocOption @pocSelect='pocSelect' ></pocOption>
  </el-form-item> -->

  <el-form-item label="扫描备注:" prop="desc">
    <el-input type="textarea" placeholder="备注信息" v-model="ruleForm.desc"></el-input>
  </el-form-item>

  <el-form-item>
    <el-button type="primary" @click="submitForm('ruleForm')">创建</el-button>
    <el-button @click="resetForm('ruleForm')">取消</el-button>
  </el-form-item>
</el-form>
  <!-- <pocOption></pocOption> -->

</div>
</template>

<script>
import {addTask, TagFetch} from '@/api/api'
const pocOption = () => import('./pocOption')

export default {
  props: {
    onQuery: {
      type: Function,
      default: null
    }
  },
  data () {
    return {
      ruleForm: {
        name: '',
        target: '',
        BBScan: false,
        tag_name: 'Default',
        port: '',
        poc: '',
        desc: ''
      },
      tags: [],
      pocs: [],
      pocRows: [],
      rules: {
        name: [
          { required: true, message: '请输入任务名称', trigger: 'blur' },
          { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
        ],
        target: [
          { required: true, message: '请输入扫描目标', trigger: 'change' }
        ]
        // date1: [
        //   { type: 'date', required: true, message: '请选择日期', trigger: 'change' }
        // ],
        // date2: [
        //   { type: 'date', required: true, message: '请选择时间', trigger: 'change' }
        // ],
        // port: [
        //   { type: 'array', required: true, message: '请至少选择一个活动性质', trigger: 'change' }
        // ],
        // resource: [
        //   { required: true, message: '请选择活动资源', trigger: 'change' }
        // ]
        // desc: [
        //   { required: true, message: '请填写活动形式', trigger: 'blur' }
        // ]
      }
    }
  },
  methods: {
    submitForm (formName) {
      this.pocs = []
      // this.pocRows = []
      // console.log(11111)
      // console.log(this.pocRows)
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.pocRows.forEach(row => {
            this.pocs.push(row.poc)
          })
          // console.log(this.ruleForm)
          const param = {
            'task_name': this.ruleForm.name,
            'task_target': this.ruleForm.target,
            'BBScan': this.ruleForm.BBScan,
            'port': this.ruleForm.port,
            'tag_name': this.ruleForm.tag_name,
            'task_desc': this.ruleForm.desc,
            'pocs': this.pocs
          }
          addTask(param)
          // console.log(this.pocs)
          this.$refs.PocOptionItemForm.clearSellect()

          this.onQuery()
          // console.log(this.pocs)
        } else {
          console.log('error submit!!')
          return false
        }
      })

      // console.log(this.pocs)
    },
    resetForm (formName) {
      // this.$refs[formName].resetFields()
      this.$emit('resetFlag', false)
      // this.$refs['refsElTable'].resetFields()
      this.pocRows = []
      this.pocs = []
      this.$refs.PocOptionItemForm.clearSellect()
    },
    pocSelect (val) {
      // console.log(val)
      this.pocRows = val // 子组件传递给父组件
      // val.forEach(row => {
      //   this.pocs.push(row.poc)
      // })
    },
    getTags () {
      TagFetch().then(res => {
        const data = res.data.entry
        console.log(data)
        for (const k in data) {
          // console.log(data[k].tag_name)
          this.tags.push({
            label: data[k].tag_name,
            value: data[k].tag_name
          })
        }
      })
    }
  },

  components: {
    pocOption
  },
  mounted: function () {
    this.getTags()
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import '~@/styles/main.scss';
</style>
