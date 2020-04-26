<template>
<div class='main-div-container'>
<el-form
    :inline="true"
    :model="query"
    @keyup.enter.native="onQuery"
    class="demo-form-inline"
    style="margin-top:15px;text-align:left"
    size="small">
    <el-form-item label="爬虫类型">
    <el-select v-model="query.type"  clearable placeholder="请选择爬虫类型">
      <el-option
        v-for="vulType in vulTypes"
        :key="vulType.value"
        :label="vulType.label"
        :value="vulType.value">
        <!-- <span style="float: left">{{ vulType.value }}({{ vulType.value }})</span> -->
        <!-- <span style="float: left">{{ vultype.label }}</span> -->
      <!-- <span style="float: right; color: #8492a6; font-size: 13px">{{ vultype.value }}</span> -->
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item label="URL">
    <el-input v-model="query.url" clearable auto-complete="true" placeholder="请输入IP或者域名"></el-input>
  </el-form-item>
  <el-form-item label="Title">
    <el-input v-model="query.title" clearable placeholder="请输入title"></el-input>
  </el-form-item>
  <el-form-item>
    <el-button type="primary" @click="onQuery">查询</el-button>
    <el-button  @click="onReset">重置</el-button>
    <el-button type="success" @click="onCopy">复制敏感URL</el-button>
  </el-form-item>
</el-form>
  <el-table
    :data="tableData"
    style="width: 100%">
    <el-table-column
      label="爬虫类型"
      prop="vul_Type"
      width="100">
    </el-table-column>
      <el-table-column
      label="URL"
      prop="url"
      width="200">
    </el-table-column>
    <el-table-column
      label="敏感URL"
      prop="vul_url"
      width="400">
    </el-table-column>
    <el-table-column
      label="Title"
      prop="title"
      width="200">
    </el-table-column>
    <el-table-column
      label="状态码"
      prop="status"
      width="100">
    </el-table-column>

    <el-table-column
      label="初次发现时间"
      sortable
      prop="first_find_date"
      width="200">
    </el-table-column>
    <el-table-column
      label="最新发现时间"
      sortable
      prop="last_find_date"
      width="200">
    </el-table-column>
    <!-- <el-table-column
      label="标签"
      prop="tag">
    </el-table-column> -->
  </el-table>
<div class="block">
      <el-pagination
        :current-page="currentPage"
        :page-sizes="[10, 50, 100, 1000]"
        :page-size="pageSize"
        :total="listTotal"
        layout="total, sizes, prev, pager, next, jumper"
        style="float:right; margin-right:50px;margin-top:10px;margin-bottom:55px"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
</div>
</div>
</template>
<script>
import {
  queryTagDetail
} from '@/api/api'

export default {
  props: {
    onValueChange: {
      type: Function,
      default: function (value) {
        console.log('undo')
      }
    }
  },
  data () {
    return {
      query: {
        type: '',
        url: '',
        title: ''
      },
      tag_name: this.$route.params.tag_name,
      tabName: 'bbscan',
      tableData: [],
      vulTypes: [],
      vuls: '',
      currentPage: 1,
      listTotal: 20,
      pageSize: 10
    }
  },
  mounted () {
    // console.log(this.taskid)
    const param = this.generateParam()
    this.initQuery(param)
    // this.queryDetail(param)
    // this.getVulTypes()
  },
  methods: {
    onQuery () {
      this.currentPage = 1
      const param = this.generateParam()
      this.queryDetail(param)
    },
    onReset () {
      this.query = {
        type: '',
        url: '',
        title: ''

      }
      this.currentPage = 1
      this.pageSize = 10
      const param = this.generateParam()
      this.queryDetail(param)
    },
    onCopy () {
      var res = []
      for (const k in this.tableData) {
        res.push(this.tableData[k]['vul_url'])
        // console.log(this.tableData[k]['vul_url'])
      }
      if (res === '') {
        this.$message.error('复制内容为空')
        return
      }
      this.vuls = res.join('\n')
      this.$copyText(this.vuls).then(res => {
        this.$message.success('URL已复制到剪切板')
      }).catch(() => {
        this.$message.error('内容复制失败')
      })
      this.vuls = ''
      // this.vuls = []
      // console.log(this.vuls)
    },

    generateParam () {
      const param = {
        pageSize: this.pageSize,
        currentPage: this.currentPage,
        query: {
          type: this.query.type,
          url: this.query.url,
          title: this.query.title
        },
        tag_name: this.tag_name,
        plugin_name: this.tabName
      }
      return param
    },
    initQuery (param) {
      queryTagDetail(param).then(res => {
        const data = res.data
        this.tableData = data.entry
        this.listTotal = data.total
        this.onValueChange(data.total)
        // console.log(data.types)
        for (const k in data.types) {
          this.vulTypes.push({
            label: data.types[k],
            value: data.types[k]
          })
        }
        // console.log(this.vulTypes)
      })
    },
    queryDetail (param) {
      queryTagDetail(param).then(res => {
        const data = res.data
        this.tableData = data.entry
        this.listTotal = data.total
        // console.log(data.types)
      })
    },
    handleSizeChange (val) {
      this.pageSize = val
      this.currentPage = 1
      const param = this.generateParam()
      this.queryDetail(param)
    },
    handleCurrentChange (val) {
      this.currentPage = val
      const param = this.generateParam()
      this.queryDetail(param)
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import '~@/styles/main.scss';
</style>
