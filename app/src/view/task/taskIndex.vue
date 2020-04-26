 <template>
 <div>

 <div class='main-div-container'>
   <el-button type="primary" @click="createTaskFlag=true" icon="el-icon-edit" size="small" style="margin-top:10px;float: left;">增加任务</el-button>
        <el-dialog
        id="device-dialog"
        :visible.sync="createTaskFlag"
        :before-close="handleClose"
        :modal-append-to-body="false"
        title="增加扫描任务"
        width="60%"
        class="device-dialog"
        >
        <createTask @resetFlag="resetFlag" :on-query="onQuery" ref="CreateTaskItem"></createTask>
        </el-dialog>

   <el-form :inline="true" :model="query" class="demo-form-inline" style="margin-left:20px;margin-top:10px;float:left;" size="small">

       <el-form-item label="任务名称">
         <el-input v-model="query.task_name" clearable auto-complete="true" placeholder="输入任务名称(模糊查询)"></el-input>
       </el-form-item>
       <el-form-item label="任务ID">
         <el-input v-model="query.task_id" clearable auto-complete="true" placeholder="输入任务ID"></el-input>
       </el-form-item>
      <!-- <el-form-item label="扫描的HOST">
         <el-input v-model="query.host" clearable auto-complete="true" placeholder="输入IP或域名"></el-input>
       </el-form-item> -->
       <el-form-item >

      <el-button type="primary" @click="onQuery">查询</el-button>
      <el-button  @click="onReset">重置</el-button>
    </el-form-item>
   </el-form>
   <el-table
    :data="tableData"
    :stripe="true"
     ref='refTable'
    style="width: 100%;margin-top:20px">
    <el-table-column type="expand">
      <template slot-scope="props">
        <el-form label-position="left" inline class="demo-table-expand">
           <el-form-item>

              <router-link style="color: rgb(51, 138, 255)" target="_blank" :to="'/task/targets/'+props.row.task_id">
              已扫描目标({{props.row.hostCount}})
              </router-link>
           <!-- <a target="_blank" :href="scope.row.vul_url" >{{scope.row.vul_url}}</a> -->
          <!-- <el-button type="text" style="margin:0" @click="copyTarget(props.row.task_target)">复制扫描目标({{props.row.task_target | generateLength}})</el-button> -->
          <!-- <pre v-highlightjs><code class="html"><div class="text-wrapper">{{props.row.task_target | generatetaskTarget}}</div></code></pre> -->
          </el-form-item>
          <el-form-item style="margin-left:100px">
            <el-button type="text" style="margin:0" disabled>扫描POC</el-button>
            <pre v-highlightjs><code class="html"><div class="text-wrapper">{{props.row.pocs| generatetaskTarget}}</div></code></pre>
            <!-- <div style="white-space: pre-line">{{ props.row.vul_response }}</div> -->
          </el-form-item>
        </el-form>
      </template>
    </el-table-column>
    <el-table-column
      label="任务ID"
      prop="task_id"
      width="300">
        <template slot-scope="scope">
          <router-link :to="'/task/'+scope.row.task_id">
            {{scope.row.task_id}}
          </router-link>
        </template>
    </el-table-column>
    <el-table-column
      label="任务名称"
      align="center"
      class="hide"
      prop="task_name"
      >
        <template slot-scope="scope">
          <el-tooltip effect="dark" :content="scope.row.task_name" placement="top">
          <span>{{scope.row.task_name | ellipsis}}</span>
          </el-tooltip>
        </template>
    </el-table-column>
    <el-table-column
      label="分组"
      align="center"
      prop="tag_name"
      >
    </el-table-column>

    <el-table-column
      label="扫描结果"
      align="center"
      header-align="center"
      prop="task_res"
      width="300"
      >
      <template slot-scope="scope">
        <el-tag size="medium"  effect="dark"  :type="getElTagType(scope.row.vulnCount,'danger')" >
         <router-link  style="color: rgb(77, 85, 93)"  :to="{name: 'taskDetail', params: {tab: 'vuln', task_id: scope.row.task_id}}">漏洞({{scope.row.vulnCount | generateCount}})
          </router-link></el-tag>

          <el-tag size="medium"  effect="dark" :type="getElTagType(scope.row.BBScanCount,'')">
          <router-link style="color: rgb(77, 85, 93)" :to="{name: 'taskDetail', params: {tab: 'bbscan', task_id: scope.row.task_id}}">爬虫({{scope.row.BBScanCount | generateCount}})
          </router-link>
          </el-tag>

        <el-tag size="medium"  effect="dark" :type="getElTagType(scope.row.DevicesCount,'success')">
          <router-link style="color: rgb(77, 85, 93)" :to="{name: 'taskDetail', params: {tab: 'devices', task_id: scope.row.task_id}}">资产({{scope.row.DevicesCount | generateCount}})
          </router-link>
        </el-tag>
      </template>
    <!-- </template> -->
                                <!-- <router-link :to="{name:'index',query:{tag:leakageInfo.tag}}">{{leakageInfo.tag}}
                                </router-link> -->

    </el-table-column>
    <el-table-column
      label="操作"
      prop="task_desc"
      align="center"
      >
      <template slot-scope="scope">
            <el-button type="text" size="small" style="margin:0" @click="handleReplay(scope.row.task_id)">重扫</el-button>
            <el-button type="text" size="small" style="margin:0" @click="handleDel(scope.row.task_id)">删除</el-button>
            <!-- <el-button type="text" size="small" style="margin:0" @click="handleReplay(scope.row.task_id)">编辑</el-button>

            <el-button type="text" size="small" style="margin:0" @click="copyTarget(scope.row.task_target)">目标</el-button> -->
      </template>
    </el-table-column>
    <el-table-column
      label="扫描时间"
      prop="task_add_date"
      align="center"
      sortable
      width="200"
      >
    </el-table-column>

    <el-table-column
      label="目录爬虫"
      prop="BBScan_flag"
      >
    <template slot-scope="scope">
      <el-switch  v-model="scope.row.BBScan_flag" disabled></el-switch>
    </template>
    </el-table-column>

    <el-table-column
      label="扫描端口"
      prop="ports">
    </el-table-column>

    <el-table-column
      label="任务备注"
      prop="task_desc">
      <!-- <template slot-scope="scope"> -->
        <!-- <span v-if="!editing" @dblclick="edit"> scope.row.task_desc</span> -->
        <!-- <el-input type="text" v-model="scope.row.task_desc" v-if="editing" :value="scope.row.task_desc" @blur=save></el-input> -->
      <!-- </template> -->
    </el-table-column>

  </el-table>

      <el-pagination
        :current-page="currentPage"
        :page-sizes="[10, 20, 30, 50]"
        :page-size="pageSize"
        :total="listTotal"
        layout="total, sizes, prev, pager, next, jumper"
        style="float:right; margin-right:100px;margin-top:15px;margin-bottom:55px"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />

</div>
</div>
</template>

<script>
import createTask from './task'
import {queryTask, replayTaskApi, delTask} from '@/api/api'

export default {
  components: {
    createTask
  },
  filters: {
    ellipsis (value) {
      if (!value) return ''
      if (value.length > 15) {
        return value.slice(0, 15) + '...'
      }
      return value
    },
    generateLength: function (value) {
      if (value !== undefined && value !== '' && value > 0) {
        return value.length
      }
      return 0
    },

    generateCount: function (value) {
      if (value !== undefined && value !== '' && value > 0) {
        return value
      }
      return 0
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
  data () {
    return {
      createTaskFlag: false,
      query: {
        task_name: '',
        task_id: ''
      },
      ok: true,
      tableData: [],
      vulnCount: 0,
      BBScanCount: 0,
      DevicesCount: 0,
      currentPage: 1,
      listTotal: 20,
      pageSize: 10
    }
  },
  methods: {
    rowClick (row, column, event) {
      this.$refs.refTable.toggleRowExpansion(row)
    },
    onSubmitAdd () {
    //   this.deviceDialogFla: true
    },
    closeDialog (val) {
      this.createTaskFlag = val
    },
    // createTask () {
    //   this.createTaskFlag = true

    //   this.onQuery()
    // },
    copyTarget (val) {
      this.$copyText(val.join('\n'))
      this.$message.success('扫描目标已复制到剪切版')
    },

    copyTarget2 (val) {
      this.$confirm('是否复制扫描目标到剪切版?', {
        confirmButtonText: '确定复制',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          // console.log(val)
          // var data = ''
          // for (const k in val) {
          //   console.log(val[k])
          //   data += val[k] + '\n'
          //   // console.log(this.tableData[k]['vul_url'])
          // }
          // data = data.replace(/[\n\r]+/g, '')
          this.$copyText(val.join('\n'))
          this.$message.success('扫描目标已复制到剪切版')
        })
        .catch(() => {
          this.$message.info('已取消复制')
        })
      // console.log(val)
    },

    handleReplay (val) {
      this.$confirm('是否重复执行该扫描任务?', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          const param = {
            task_id: val
          }
          replayTaskApi(param).then(res => {
            const flag = res.data['msg']
            if (flag === 'ok') {
              this.$message.success('Success 任务重新执行中')
              this.onReset()
            } else {
              this.$message.error('复制任务失败')
            }
          })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '已取消'
          })
        })
    },
    handleDel (val) {
      this.$confirm('是否删除改任务(包括端口，漏洞，爬虫)?', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          const param = {
            task_id: val
          }
          delTask(param).then(res => {
            const flag = res.data['msg']
            if (flag === 'ok') {
              this.$message.success('任务删除成功')
              this.onReset()
            } else {
              this.$message.error(res.data.msg)
            }
          })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '已取消'
          })
        })
    },
    handleClose () {
      this.$confirm('确认关闭？')
        .then(_ => {
          this.$refs.CreateTaskItem.resetForm()
        })
    },
    resetFlag (val) {
      this.createTaskFlag = val
    },
    onQuery () {
      this.resetFlag(false)
      this.currentPage = 1
      // console.log(this.query)
      const param = this.generateParam()
      this.task_query(param)
    },
    onReset () {
      this.query = {
        task_name: '',
        task_id: ''

      }
      this.currentPage = 1
      this.pageSize = 10
      const param = this.generateParam()
      this.task_query(param)
    },
    generateParam () {
      const param = {
        pageSize: this.pageSize,
        currentPage: this.currentPage,
        task_name: this.query.task_name,
        task_id: this.query.task_id
        // level: this.query.level,
        // category: this.query.category
      }
      return param
    },
    task_query (param) {
      queryTask(param).then(res => {
        const data = res.data
        this.tableData = data.entry
        // for (const key in this.tableData) {
        //   this.tableData[key].BBScanCount = 10
        // }
        this.listTotal = data.total
        // this.vulnCount = data.vulnCount
        this.BBScanCount = data.BBScanCount
        this.DevicesCount = data.DevicesCount
      })
    },
    handleSizeChange (val) {
      this.pageSize = val
      this.currentPage = 1
      const param = this.generateParam()
      this.task_query(param)
    },
    handleCurrentChange (val) {
      this.currentPage = val
      const param = this.generateParam()
      this.task_query(param)
    },
    getElTagType (value, originType) {
      // if (value !== undefined && value > 0) {
      if (value > 0) {
        return originType
      }
      return 'info'
    }
    // test () {
    //   test()
    // }
  },
  mounted () {
    const param = this.generateParam()
    this.task_query(param)
    console.log(this.$route)
    // console.log(this.vulnCount)
  }
}
</script>
<style rel="stylesheet/scss" lang="scss" scoped>
@import '~@/styles/main.scss';

a {
  text-decoration: none;
}

.router-link-active {
  text-decoration: none;
}

.text-wrapper {
  white-space: pre-line;
  line-height: 23px;
  margin-top: 6px;
}

</style>
