<template>
<!-- <DashBoard></Dashboard> -->

<!-- <NavMenu>222</NavMenu> -->
<div class='main-div-container'>
  <!-- <NavMenu></NavMenu> -->
  <el-form :inline="true" :model="query" class="demo-form-inline" style="margin-top:15px;text-align:left" size="small">
       <el-form-item label="服务">
        <el-select v-model="query.server"  clearable placeholder="请选择运行的服务">
      <el-option
        v-for="s in servers"
        :key="s.value"
        :label="s.label"
        :value="s.value">
        <!-- <span style="float: left">{{ vultype.label }}</span> -->
      <!-- <span style="float: right; color: #8492a6; font-size: 13px">{{ vultype.value }}</span> -->
      </el-option>
    </el-select>
  </el-form-item>

    <el-form-item label="主机">
    <el-input v-model="query.ip" clearable auto-complete="true" placeholder="请输入IP或者域名"></el-input>
    </el-form-item>

    <el-form-item label="端口">
    <el-input v-model="query.port" clearable auto-complete="true" placeholder="请输入端口号"></el-input>
    </el-form-item>

    <!-- <el-form-item label="服务">
    <el-input v-model="query.server" clearable auto-complete="true" placeholder="请输入运行的服务"></el-input>
    </el-form-item> -->

    <el-form-item label="HTTP状态码">
    <el-input v-model="query.status_code" clearable auto-complete="true" placeholder="请输入WEB服务状态码"></el-input>
    </el-form-item>

    <el-form-item label="HTTP的Title">
    <el-input v-model="query.title" clearable auto-complete="true" placeholder="请输入WEB服务title"></el-input>
    </el-form-item>

    <!-- <el-form-item label="HTTP的Title">
    <el-input v-model="query.title" clearable auto-complete="true" placeholder="请输入WEB服务title"></el-input>
    </el-form-item> -->
    <el-form-item label="Body">
    <el-input v-model="query.banner" clearable auto-complete="true" placeholder="请输入WEB服务Banner"></el-input>
    </el-form-item>

    <!-- <br> -->
    <el-form-item style="margin-left:50px">

      <el-button type="primary" @click="onQuery">查询</el-button>
      <el-button type="" @click="onReset">重置</el-button>
      <el-button type="success" @click="onCopy">复制主机:端口</el-button>
    </el-form-item>
   <!-- <div class="block"> -->

  <!-- </div> -->
  </el-form>
  <el-table
    :data="tableData"
    ref='refTable'
    >
    <el-table-column type="expand">
      <template slot-scope="props">
        <el-form label-position="left" inline class="demo-table-expand">
          <pre v-highlightjs><code class="html">{{props.row.banner}}</code></pre>
        </el-form>
      </template>
    </el-table-column>
    <el-table-column
      label="域名"
      prop="url"
      width="200">
    </el-table-column>
    <el-table-column
      label="IP"
      prop="ip"
      width="200">
    </el-table-column>
    <el-table-column
      label="端口"
      sortable
      prop="port"
      width="150">
    </el-table-column>
    <el-table-column
      label="服务"
      sortable
      prop="server"
      width="100">
    </el-table-column>
        <el-table-column
      label="Product"
      prop="product"
      width="200">
    </el-table-column>
    <el-table-column
      label="HTTP状态码"
      sortable
      prop="status_code">
    </el-table-column>
    <el-table-column
      label="HTTP的Title"
      prop="title"
      width="200">
    </el-table-column>
>
    <!-- <el-table-column
      label="HTTP的Banner"
      prop="banner"
      width="200">
    </el-table-column> -->
    <el-table-column
      label="初次发现时间"
      sortable
      prop="first_find_date"
      width="150">
    </el-table-column>
    <el-table-column
      label="最新发现时间"
      sortable
      prop="last_find_date"
      width="150">
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
  data () {
    return {
      query: {
        server: '',
        ip: '',
        port: '',
        status_code: '',
        title: '',
        banner: ''
      },
      tag_name: this.$route.params.tag_name,
      tabName: 'device',
      tableData: [],
      servers: [],
      hosts: '',
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
        server: '',
        ip: '',
        port: '',
        status_code: '',
        title: '',
        banner: ''

      }
      this.currentPage = 1
      this.pageSize = 10
      const param = this.generateParam()
      this.queryDetail(param)
    },
    onCopy () {
      var res = []
      for (const k in this.tableData) {
        res.push(this.tableData[k]['ip'] + ':' + this.tableData[k]['port'])
        // console.log(this.tableData[k]['vul_url'])
      }
      if (this.tableData[0]['ip'] === '') {
        this.$message.error('复制内容为空')
        return
      }
      this.hosts = res.join('\n')
      this.$copyText(this.hosts).then(res => {
        this.$message.success('主机已复制到剪切板')
      }).catch(() => {
        this.$message.error('内容复制失败')
      })
      this.hosts = ''
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
          server: this.query.server,
          ip: this.query.ip,
          port: this.query.port,
          status_code: this.query.status_code,
          title: this.query.title,
          banner: this.query.banner
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
        for (const k in data.servers) {
          this.servers.push({
            label: data.servers[k],
            value: data.servers[k]
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
