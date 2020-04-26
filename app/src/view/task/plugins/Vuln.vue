<template>
<!-- <DashBoard></Dashboard> -->

<!-- <NavMenu>222</NavMenu> -->
<div class='main-div-container'>
  <!-- <NavMenu></NavMenu> -->
<!-- <DashBoard></DashBoard> -->
  <el-dialog
    :visible.sync="dialogFormVisible"
    title='修改备注'
    width="30%"
    >
            <el-form :model="form">
            <el-input
            type="textarea"
            :rows=8
            v-model="form.vul_desc"
            ></el-input>
            </el-form>

              <div style="margin-top:9px">
                <el-button round size="mini" @click="dialogFormVisible = false">取 消</el-button>
                <el-button round size="mini" type="primary" @click="handleAddDesc(form)">确 定</el-button>
              </div>
  </el-dialog>

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
  <el-form-item label="域名">
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
            <!-- <span>{{ props.row.vul_url }}</span> @row-click="rowClick"-->
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
      label="域名"
      prop="vul_url"
      width="300">
      <template slot-scope="scope">
          <a target="_blank" :href="scope.row.vul_url" >{{scope.row.vul_url}}</a>
      </template>
    </el-table-column>
    <el-table-column
      label="操作"
      align="center"
      prob="vul_desc"
      width="100">
      <template slot-scope="scope">
            <el-button type="text" size="small" style="margin:0" @click="handleDialog(scope.row)">备注</el-button>
            <el-button type="text" size="small" style="margin:0" @click="handleAddBlack(scope.row)">拉黑</el-button>
      </template>
    </el-table-column>
    <el-table-column
      label="POC"
      prop="poc"
      width="100">
    </el-table-column>
    <el-table-column
      label="备注"
      prop="vul_desc"
      width=300>
        <template slot-scope="scope">

          <el-tooltip effect="dark" :content="scope.row.vul_desc" placement="top">
          <div v-html="ToBreak(scope.row.vul_desc)" slot="content"></div>
          <span>{{scope.row.vul_desc | ellipsis}}</span>
          <!-- <div class="oneLine">{{scope.row.vul_desc}}</div> -->
          <!-- <pre v-highlightjs><code class="html">{{scope.row.vul_desc | ellipsis}}</code></pre> -->
          </el-tooltip>
        </template>
    </el-table-column>
    <el-table-column
      label="漏洞等级"
      prop="level"
      width=100>
    </el-table-column>
    <el-table-column
      label="漏洞类型"
      prop="type"
      width="250">
    </el-table-column>
    <el-table-column
      label="发现时间"
      sortable
      prop="first_find_date">
    </el-table-column>
    <!-- <el-table-column
      label="最新发现时间"
      sortable
      prop="last_find_date">
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
  queryTaskId, addVulDesc, addVulBlack
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
  filters: {
    ellipsis (value) {
      if (!value) return ''
      if (value.length > 15) {
        return value.slice(0, 15) + '...'
      }
      return value
    }
  },
  data () {
    return {
      form: {
        task_id: '',
        vul_url: '',
        poc: '',
        vul_desc: ''
      },
      dialogFormVisible: false,
      query: {
        type: '',
        url: '',
        port: '',
        tag: ''
      },
      task_id: this.$route.params.task_id,
      tabName: 'vuln',
      tableData: [],
      vulTypes: [],
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
    // rowClick (row, column, event) {
    //   this.$refs.refTable.toggleRowExpansion(row)
    // },
    handleDialog (val) {
      this.dialogFormVisible = true

      this.form.task_id = val.task_id
      this.form.vul_url = val.vul_url
      this.form.poc = val.poc
      this.form.vul_desc = val.vul_desc
    },
    handleAddDesc (val) {
      let param = ''
      param = {
        // task_id: val.task_id,
        vul_url: val.vul_url,
        poc: val.poc,
        vul_desc: val.vul_desc

      }
      addVulDesc(param)
      this.dialogFormVisible = false
      this.onQuery()
    },

    handleAddBlack (val) {
      this.$confirm('是否拉黑? 拉黑之后无法查看', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let param = ''
          param = {
            vul_url: val.vul_url,
            poc: val.poc
          }
          addVulBlack(param).then(res => {
            if (res.data.msg === 'ok') {
              this.$message.success('Sunccess')
              this.onQuery()
            } else {
              this.$message.error(res.data.msg)
            }
          })
        })
    },

    ToBreak (val) {
      if (val !== undefined) {
        return val.split('\n').join('<br/>')
        // return val.replace('\n', '<br />')
      }
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
        task_id: this.task_id,
        plugin_name: this.tabName
      }
      return param
    },
    initQuery (param) {
      queryTaskId(param).then(res => {
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
      queryTaskId(param).then(res => {
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
.oneLine {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
</style>
