<template>
<!-- <DashBoard></Dashboard> -->

<!-- <NavMenu>222</NavMenu> -->
<div class='main-div-container'>
  <!-- <NavMenu></NavMenu> -->
<!-- <DashBoard></DashBoard> -->
<el-form :inline="true" :model="query" class="demo-form-inline" style="margin-top:15px;text-align:left" size="small">
    <el-form-item label="漏洞类型">
    <el-select v-model="query.type"  clearable placeholder="请选择漏洞类型">
      <el-option
        v-for="vulType in vulTypes"
        :key="vulType.value"
        :label="vulType.label"
        :value="vulType.value">
        <!-- <span style="float: left">{{ vultype.label }}</span> -->
      <!-- <span style="float: right; color: #8492a6; font-size: 13px">{{ vultype.value }}</span> -->
      </el-option>
    </el-select>
  </el-form-item>
  <el-form-item label="主机">
    <el-input v-model="query.url" clearable auto-complete="true" placeholder="请输入IP或者域名"></el-input>
  </el-form-item>
  <el-form-item label="端口">
    <el-input v-model="query.port" clearable placeholder="请输入端口号"></el-input>
  </el-form-item>
  <el-form-item>
    <el-button type="primary" @click="onQuery">查询</el-button>
    <el-button  @click="onReset">重置</el-button>
  </el-form-item>
</el-form>
  <el-table
    :data="tableData"
     ref='refTable'
    style="width: 100%">
    <el-table-column type="expand">
      <template slot-scope="props">
        <el-form label-position="left" inline class="demo-table-expand">
          <el-form-item label="Request">
            <!-- <span>{{ props.row.vul_url }}</span> -->
            <pre v-highlightjs><code class="html">{{props.row.vul_url}}</code></pre>
          </el-form-item>
          <el-form-item label="Response">
            <pre v-highlightjs><code class="html">{{props.row.vul_response}}</code></pre>
            <!-- <div style="white-space: pre-line">{{ props.row.vul_response }}</div> -->
          </el-form-item>
        </el-form>
      </template>
    </el-table-column>
    <el-table-column
      label="主机"
      prop="url"
      width="200">
    </el-table-column>
    <el-table-column
      label="端口"
      prop="port"
      width="100">
    </el-table-column>
    <el-table-column
      label="POC"
      prop="poc"
      width="100">
    </el-table-column>
    <el-table-column
      label="漏洞名称"
      prop="name">
    </el-table-column>
    <el-table-column
      label="漏洞等级"
      prop="level">
    </el-table-column>
    <el-table-column
      label="漏洞类型"
      prop="type">
    </el-table-column>
    <el-table-column
      label="初次发现时间"
      sortable
      prop="first_find_date">
    </el-table-column>
    <el-table-column
      label="最新发现时间"
      sortable
      prop="last_find_date">
    </el-table-column>
    <el-table-column
      label="标签"
      prop="tag">
    </el-table-column>
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
  // props: {
  //   taskid: {
  //     type: String,
  //     default: null
  //   }
  // },
  data () {
    return {
      query: {
        type: '',
        url: '',
        port: '',
        tag: ''
      },
      tag_name: this.$route.params.tag_name,
      tabName: 'vuln',
      tableData: [],
      vulTypes: [],
      currentPage: 1,
      listTotal: 0,
      pageSize: 10
    }
  },
  mounted () {
    // console.log(this.taskid)
    this.currentPage = 1
    this.pageSize = 10
    const param = this.generateParam()
    this.queryDetail(param)
    // this.queryDetail(param)
    // this.getVulTypes()
  },
  methods: {
    rowClick (row, column, event) {
      this.$refs.refTable.toggleRowExpansion(row)
    },
    onQuery () {
      this.currentPage = 1
      const param = this.generateParam()
      this.queryDetail(param)
    },
    onReset () {
      this.query = {
        type: '',
        url: '',
        port: '',
        tag: ''

      }
      this.currentPage = 1
      this.pageSize = 10
      const param = this.generateParam()
      this.queryDetail(param)
    },
    // getVulTypes () {
    //   getTypes().then(res => {
    //     const data = res.data
    //     // console.log(data)
    //     for (const k in data) {
    //       console.log(data[k])
    //       this.vulTypes.push({
    //         label: data[k],
    //         value: data[k]
    //       })
    //     }
    //     // console.log(this.vulTypes)
    //   })
    // },
    generateParam () {
      const param = {
        pageSize: this.pageSize,
        currentPage: this.currentPage,
        query: {
          type: this.query.type,
          url: this.query.url,
          port: this.query.port,
          tag: this.query.tag
        },
        tag_name: this.tag_name,
        plugin_name: this.tabName
      }
      return param
    },
    queryDetail (param) {
      queryTagDetail(param).then(res => {
        const data = res.data
        this.tableData = data.entry
        this.listTotal = data.total
        this.onValueChange(data.total)
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
    // mounted () {
    //   this.$emit('vulCount', this.listTotal)
    //   console.log(this.listTotal)
    // }

  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import '~@/styles/main.scss';
</style>
