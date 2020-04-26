<template>
<div>
    <div class="breadcrumb" v-if="$route.path!=='/'">
            <el-breadcrumb separator-class="el-icon-arrow-right">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item>{{$route.meta.name}}</el-breadcrumb-item>
            </el-breadcrumb>
  </div>
<div class='main-div-container'>
        <el-dialog
        id="tag-dialog"
        :visible.sync="dialogFormVisible"
        v-model="dialogFormVisible"
        title="增加域名分组"
        width="50%"
        class="device-dialog"
        >
        <el-form :model="form">
            <el-form-item label="分组名称:">
            <el-input v-model="form.tag_name"></el-input>
            </el-form-item>
            <el-form-item label="分组描述:">
            <el-input v-model="form.tag_desc"></el-input>
            </el-form-item>
        </el-form>
                <div slot="footer" class="dialog-footer">
                <el-button round size="mini" @click="dialogFormVisible = false">取 消</el-button>
                <el-button round size="mini" type="primary" @click="handleAddQuery(form)">确 定</el-button>
                </div>
        </el-dialog>

        <el-button type="primary" size="mini" @click="dialogFormVisible = true" style="float:left;margin-bottom:15px">
            增加标签
        </el-button>

        <el-table :data="tableData" :stripe="true" ref='refTable'>
            <!-- <el-table-column type="expand">
              <template slot-scope="props">
                <el-form label-position="left" inline class="demo-table-expand">
                 <el-form-item>
                      <router-link style="color: rgb(51, 138, 255)" target="_blank" :to="'/group/targets/'+props.row.tag_name">
                        已扫描目标()
                      </router-link>
                </el-form-item>
                </el-form>
              </template>
            </el-table-column> -->
            <el-table-column
            label="分组标签"
            prop="tag_name"
            width="200">
            </el-table-column>
            <el-table-column
            label="分组描述"
            prop="tag_desc"
            >
            </el-table-column>
            <el-table-column
            label="主机数量"
            prop="hostCount"
            align="center"
            width=200>
                <template slot-scope="scope">
                  <router-link style="color: rgb(51, 138, 255)" target="_blank" :to="'/group/targets/'+scope.row.tag_name">
                  {{scope.row.hostCount}}
                  </router-link>
                </template>
            </el-table-column>
            <el-table-column
            label="扫描结果"
            align="center"
            header-align="center"
            width="300"
            >
              <template slot-scope="scope">
                   <el-tag size="medium"  effect="dark"  :type="getCountColor(scope.row.vulCount,'danger')" >
                      <router-link style="color: rgb(77, 85, 93)" :to="{name: 'tagDetail', params: {tab: 'vuln', tag_name: scope.row.tag_name}}">
                        漏洞{{scope.row.vulCount | generateCount}}
                      </router-link></el-tag>

                     <el-tag size="medium"  effect="dark"  :type="getCountColor(scope.row.spiderCount,'')" >
                      <router-link  style="color: rgb(77, 85, 93)" :to="{name: 'tagDetail', params: {tab: 'bbscan', tag_name: scope.row.tag_name}}">
                        爬虫{{scope.row.spiderCount | generateCount}}
                      </router-link></el-tag>

                  <el-tag size="medium"  effect="dark"  :type="getCountColor(scope.row.deviceCount,'success')" >
                      <router-link style="color: rgb(77, 85, 93)" :to="{name: 'tagDetail', params: {tab: 'devices', tag_name: scope.row.tag_name}}">
                      资产{{scope.row.deviceCount | generateCount}}
                      </router-link></el-tag>

              </template>
            </el-table-column>

            <el-table-column
            label="操作"
            width=200>
            <template slot-scope="scope">
                <el-button-group>
                    <el-button v-if="scope.row.tag_name !== 'Default'"
                              size="mini"
                              plain
                              round
                              @click="handleEdit(scope.row)">编辑
                    </el-button>
                    <el-button v-if="scope.row.tag_name !== 'Default'"
                              size="mini"
                              plain
                              round
                              type="danger"
                              @click="handleDel(scope.row)">删除
                    </el-button>
                </el-button-group>
            </template>
            </el-table-column>
        </el-table>
</div>
</div>
</template>
<script>
import {TagAdd, TagFetch, TagDel} from '@/api/api'

export default {
  data () {
    return {
      tableData: [],
      dialogFormVisible: false,
      form: {
        tag_name: '',
        tag_desc: ''
      }
    }
  },
  filters: {
    generateCount: function (value) {
      if (value !== undefined && value !== '' && value > 0) {
        return value
      }
      return 0
    },
    generateLength: function (value) {
      if (value !== 0) {
        return value.length
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

  methods: {
    // sendData (val) {
    //   this.$router.push({'name': 'taskDetail', params: {'count': val}})
    //   console.log(this.$route.param)
    // },
    rowClick (row, column, event) {
      this.$refs.refTable.toggleRowExpansion(row)
    },
    getCountColor (val, originType) {
      if (val !== undefined && val > 0) {
        return originType
      }
      return 'info'
    },
    handleEdit (row) {
      this.dialogFormVisible = true
      this.form = row
    },
    copyTarget (val) {
      this.$copyText(val.join('\n'))
      this.$message.success('扫描目标已复制到剪切版')
    },
    handleDel (row) {
      this.$confirm('是否删除该标签?', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          TagDel(row).then(res => {
            if (res.data.msg === 'ok') {
              this.$message.success('删除成功')
              this.fetchTag()
            } else {
              this.$message.error(res.data.msg)
            }
          })
        })
    },
    fetchTag () {
      TagFetch().then(res => {
        const data = res.data
        this.tableData = data.entry
      })
    },
    handleAddQuery (form) {
      TagAdd(form).then(res => {
        if (res.data.msg === 'ok') {
          this.$message.success('添加成功')
          this.dialogFormVisible = false
          this.fetchTag()
        } else {
          this.$message.success(res.data.msg)
          this.dialogFormVisible = false
          this.fetchTag()
        }
      })
      this.form = []
    }
  },
  mounted: function () {
    this.fetchTag()
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import '~@/styles/main.scss';
.router-link-active {
  text-decoration: none;
}
a {
  text-decoration: none;
}
.text-wrapper {
  white-space: pre-line;
  line-height: 22px;
  margin-top: 6px;
}
</style>
