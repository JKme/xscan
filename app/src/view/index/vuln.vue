<template>
<div>
        <div class="breadcrumb" v-if="$route.path!=='/'">
            <el-breadcrumb separator-class="el-icon-arrow-right">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item>{{$route.meta.name}}</el-breadcrumb-item>
            </el-breadcrumb>
      </div>
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
 <el-form-item label="POC">
    <el-input v-model="query.poc" clearable placeholder="请输入POC"></el-input>
  </el-form-item>

<el-form-item  label="漏洞等级">
      <el-select v-model="query.level" clearable placeholder="请选择危害等级">
        <el-option label="高" value="high"></el-option>
        <el-option label="中" value="medium"></el-option>
        <el-option label="低" value="low"></el-option>
    </el-select>
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
            <pre v-highlightjs><code class="html">{{props.row.vul_url}}</code></pre>
            <!-- <span>{{ props.row.vul_url }}</span> -->
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
      prop="vul_url"
      width="300">
      <template slot-scope="scope">
          <a target="_blank" :href="scope.row.vul_url" >{{scope.row.vul_url}}</a>
      </template>
    </el-table-column>
    <el-table-column
      label="端口"
      prop="port"
      width="100">
    </el-table-column>
    <el-table-column
      label="POC"
      prop="poc"
      align="center"
      width="100">
    </el-table-column>
    <el-table-column
      label="黑名单"
      prop="black_flag"
      align="center"
      width="100">
          <template slot-scope="scope">
            <span :style="{'color': colorChange(scope.row.black_flag)}">{{scope.row.black_flag | setBlackFlag}}</span>
            <!-- <el-switch  v-model="scope.row.black_flag" disabled></el-switch> -->
          </template>
    </el-table-column>
    <el-table-column
      label="漏洞名称"
      align="center"
      prop="name">
    </el-table-column>
    <el-table-column
      label="漏洞等级"
      align="center"
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
    <!-- <el-table-column
      label="标签"
      prop="tag">
    </el-table-column> -->
  </el-table>
<div class="block">
      <el-pagination
        :current-page="currentPage"
        :page-sizes="[10, 20, 30, 50]"
        :page-size="pageSize"
        :total="listTotal"
        layout="total, sizes, prev, pager, next, jumper"
        style="float:right; margin-right:50px;margin-top:10px;margin-bottom:55px"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
</div>
</div>
</div>
</template>
<script>
import {
  queryvul
} from '@/api/api'

export default {
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
        tag: '',
        poc: '',
        level: ''
      },
      tableData: [],
      vulTypes: [],
      currentPage: 1,
      listTotal: 20,
      pageSize: 10
    }
  },
  filters: {
    setBlackFlag (val) {
      if (val === 0) {
        return '否'
      }
      return '是'
    }
  },
  mounted () {
    // console.log(this.taskid)
    const param = this.generateParam()
    this.queryDetail(param)
    // this.queryDetail(param)
    // this.getVulTypes()
  },
  methods: {
    colorChange (value) {
      let color = ''
      if (value !== undefined && value > 0 && value !== '') {
        color = '#ff0000'
      } else {
        color = '#409eff'
      }
      return color
    },
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
        tag: '',
        poc: '',
        level: ''

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
          poc: this.query.poc,
          port: this.query.port,
          tag: this.query.tag,
          level: this.query.level
        }
      }
      return param
    },
    queryDetail (param) {
      queryvul(param).then(res => {
        const data = res.data
        this.tableData = data.entry
        this.listTotal = data.total
        // console.log(data.types)
        for (const k in data.types) {
          this.vulTypes.push({
            label: data.types[k],
            value: data.types[k]
          })
        }
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
