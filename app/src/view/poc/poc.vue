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
  <el-form :inline="true" :model="query" class="demo-form-inline" style="margin-top:15px;text-align:left" size="small">
      <el-form-item label="文件夹">
      <el-select v-model="query.folders"  clearable placeholder="请选择POC文件夹">
        <el-option
          v-for="folder in folders"
          :key="folder.value"
          :label="folder.label"
          :value="folder.value">
          <!-- <span style="float: left">{{ vultype.label }}</span> -->
        <!-- <span style="float: right; color: #8492a6; font-size: 13px">{{ vultype.value }}</span> -->
        </el-option>
      </el-select>
    </el-form-item>
    <el-form-item label="类型">
    <el-select  v-model="query.category" clearable placeholder="请选择漏洞类型">
        <el-option
          v-for="cate in category"
          :key="cate.value"
          :label="cate.label"
          :value="cate.value">
        </el-option>
    </el-select>
    </el-form-item>
    <el-form-item label="POC">
      <el-input v-model="query.poc" clearable auto-complete="true" placeholder="请输入POC (模糊查询)"></el-input>
    </el-form-item>
    <el-form-item  label="等级">
      <el-select v-model="query.level" clearable placeholder="请选择危害等级">
        <el-option label="高" value="High"></el-option>
        <el-option label="中" value="Medium"></el-option>
        <el-option label="低" value="Low"></el-option>
    </el-select>
    </el-form-item>

    <!-- <br> -->
    <el-form-item >

      <el-button type="primary" @click="onQuery">查询</el-button>
      <el-button  @click="onReset">重置</el-button>
    </el-form-item>
   <!-- <div class="block"> -->

  <!-- </div> -->
  </el-form>
  <el-table
    :data="tableData"
    style="width: 90%;">
    <el-table-column
      label="文件夹"
      prop="folder"
      width="100">
    </el-table-column>
    <el-table-column
      label="POC"
      prop="poc"
      width="200">
    </el-table-column>
    <el-table-column
      label="POC等级"
      prop="level"
      width="100">
    </el-table-column>
    <el-table-column
      label="POC分类"
      prop="category"
      width="150">
    </el-table-column>
    <el-table-column
      label="POC信息"
      prop="info"
      width="200">
    </el-table-column>
    <el-table-column
      label="POC备注"
      prop="extra"
      width="200">
    </el-table-column>
    <el-table-column
      label="修改时间"
      sortable
      prop="mtime"
      width="150">
    </el-table-column>

    <el-table-column
      label="操作"
      prop="edit">
    </el-table-column>
    <!-- <el-table-column
      label="最新修改时间"
      prop="first_find_date">
    </el-table-column> -->

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
import {initPocQuery,
  pocQuery

} from '@/api/api'

export default {
  data () {
    return {
      query: {
        folders: '',
        poc: '',
        level: '',
        category: ''
      },
      folders: [],
      category: [],
      tableData: [],
      currentPage: 1,
      listTotal: 20,
      pageSize: 10
    }
  },
  mounted () {
    const param = this.generateParam()
    this.pocQuery(param)
    this.getPocFolders()
  },
  methods: {
    onQuery () {
      this.currentPage = 1
      const param = this.generateParam()
      this.pocQuery(param)
    },
    onReset () {
      this.query = {
        folders: '',
        poc: '',
        level: '',
        category: ''

      }
      this.currentPage = 1
      this.pageSize = 10
      const param = this.generateParam()
      this.pocQuery(param)
    },
    getPocFolders () {
      initPocQuery().then(res => {
        const data = res.data['folders']
        // console.log(data)
        for (const k in data) {
        //   console.log(data[k])
          this.folders.push({
            label: data[k],
            value: data[k]
          })
        }
        const d = res.data['category']
        for (const k in d) {
          this.category.push({
            label: d[k],
            value: d[k]
          })
        }
      })
    },
    generateParam () {
      const param = {
        pageSize: this.pageSize,
        currentPage: this.currentPage,
        folders: this.query.folders,
        poc: this.query.poc,
        level: this.query.level,
        category: this.query.category
      }
      return param
    },
    pocQuery (param) {
      pocQuery(param).then(res => {
        const data = res.data
        this.tableData = data.entry
        this.listTotal = data.total
      })
    },
    handleSizeChange (val) {
      this.pageSize = val
      this.currentPage = 1
      const param = this.generateParam()
      this.pocQuery(param)
    },
    handleCurrentChange (val) {
      this.currentPage = val
      const param = this.generateParam()
      this.pocQuery(param)
    }
  }
//   components: {
//     Detail,
//     DashBoard,
//     NavMenu
//   }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
@import '~@/styles/main.scss';
</style>
