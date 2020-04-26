<template>
<div>
  <!-- <NavMenu></NavMenu> -->
<el-form :inline="true" :model="query" class="demo-form-inline" size="mini" >
    <el-form-item label="文件夹">
    <el-select v-model="query.folders"  clearable placeholder="请选择POC文件夹" label-width="10px">
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
  <el-form-item label="POC">
    <el-input v-model="query.poc" clearable auto-complete="true" placeholder="请输入POC(模糊查询)"></el-input>
  </el-form-item>
  <el-form-item  label="等级">
    <el-select v-model="query.level" clearable placeholder="请选择危害等级">
      <el-option label="高" value="High"></el-option>
      <el-option label="中" value="Medium"></el-option>
      <el-option label="低" value="Low"></el-option>
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
  <el-form-item>
    <el-button type="primary" @click="onQuery">查询</el-button>
    <el-button type="primary" @click="onReset">重置</el-button>
  </el-form-item>
   <!-- <div class="block"> -->
<el-table
    :data="tableData"
    ref="refsPOCElTable"
    style="width: 100%"
    :row-style="rowStyle"
    :row-class-name="rowClassName"

    @select-all="selectAll"
    @select="selectChange">
        <!-- @row-click="rowClick" -->
    <el-table-column
      type="selection"
      width="55">
    </el-table-column>
    <!-- <el-table-column
      type="index"
      prob="id"
      width="30">
    </el-table-column> -->
    <el-table-column
      label="文件夹"
      prop="folder"
      width="100">
    </el-table-column>
    <el-table-column
      label="POC"
      prop="poc"
      width="150">
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
    <!-- <el-table-column
      label="POC备注"
      prop="extra"
      width="200">
    </el-table-column> -->
    <!-- <el-table-column
      label="修改时间"
      sortable
      prop="mtime"
      width="150">
    </el-table-column> -->

    <!-- <el-table-column
      label="操作"
      prop="edit"
      width="200">
    </el-table-column> -->
    <!-- <el-table-column
      label="最新修改时间"
      prop="first_find_date">
    </el-table-column> -->

    <!-- <el-table-column
      label="标签"
      prop="tag">
    </el-table-column> -->
  </el-table>
<!-- </div>margin-bottom:55px -->
</el-form>

<div class="block">
      <el-pagination
        :current-page="currentPage"
        :page-sizes="[10, 20, 30, 50]"
        :page-size="pageSize"
        :total="listTotal"
        layout="total, sizes, prev, pager, next, jumper"
        style="float:right; margin-right:50px;margin-top:10px;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
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
      selectPocs: [],
      copyChooseTchIds: [],
      selectionRow: [],
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

    // handleSelectPoc (rows) {
    //   if (rows) {
    //     rows.forEach(row => {
    //       if (row.rawIndex) { this.selectPocs.push(row.poc) }
    //     })
    //   }
    // },

    rowClick (row) {
    //   let refsElTable = this.$refs.refsElTable
    //   refsElTable.toggleRowSelection(row)
      this.$refs.refsElTable.toggleRowSelection(row, true)
      console.log(row.poc)
    //   let findRow = this.selectionRow.find(c => c.rowIndex === row.rowIndex)
    //   if (findRow) {
    //     refsElTable.toggleRowSelection(row, false)
    //   }
    //   //
    //   refsElTable.clearSelection()
    //   refsElTable.toggleRowSelection(row)
    //
    },

    rowStyle ({row, rowIndex}) {
      Object.defineProperty(row, 'rowIndex', { // 给每一行添加不可枚举属性rowIndex来标识当前行
        value: rowIndex,
        writable: true,
        enumerable: false
      })
    },

    rowClassName ({ row, rowIndex }) {
      let rowName = ''
      let findRow = this.selectionRow.find(c => c.rowIndex === row.rowIndex)
      if (findRow) {
        rowName = 'current-row ' // elementUI 默认高亮行的class类 不用再样式了^-^,也可通过css覆盖改变背景颜色
      }
      return rowName // 也可以再加上其他类名 如果有需求的话
    },

    selectChange (val, row) {
    /* 1 => add ; 0 => remove */
      let flag = 0
      for (let i in val) {
        if (row.rowIndex === val[i].rowIndex) {
          flag = 1
          break
        }
      }
      if (flag === 1) {
        this.copyChooseTchIds.push(row)
      } else {
        for (let i in this.copyChooseTchIds) {
          if (this.copyChooseTchIds[i].rowIndex === row.rowIndex) {
            this.copyChooseTchIds.splice(i, 1)
          }
        }
      }
      //   console.log(this.copyChooseTchIds)
      this.$emit('pocSelect', this.copyChooseTchIds)
      // this.$nextTick(() => { this.$refs['refsElTable'].resetFields() })
      //  this.$refs.refsElTable.clearSelection()
    //   console.log(this.selectPocs)
    },

    selectAll (val) {
      var v = this
      // remove
      if (val.length === 0) {
        for (let i in v.tableData) {
          for (let j in v.copyChooseTchIds) {
            if (v.copyChooseTchIds[j].id === v.tableData[i].id) {
              v.copyChooseTchIds.splice(j, 1)
              break
            }
          }
        }
      }
      if (v.copyChooseTchIds.length === 0) {
        for (let i in val) {
          v.copyChooseTchIds.push(val[i])
        }
      } else {
        for (let i in val) {
          let flag = false
          for (let j in v.copyChooseTchIds) {
            if (v.copyChooseTchIds[j].id === val[i].id) {
              flag = true
              break
            }
          }
          if (!flag) { v.copyChooseTchIds.push(val[i]) }
        }
      }
      this.$emit('pocSelect', this.copyChooseTchIds)
      // this.refsElTable.clearSelection()
    //   console.log(this.copyChooseTchIds)
    },

    getPocFolders () {
      initPocQuery().then(res => {
        const d2 = res.data['folders']
        // console.log(d2)
        for (const k in d2) {
        //   console.log(data[k])
          this.folders.push({
            label: d2[k],
            value: d2[k]
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
    },
    clearSellect () {
      this.copyChooseTchIds = []
      this.$emit('pocSelect', [])
      this.$refs.refsPOCElTable.clearSelection()
    }
  }
//   components: {
//     Detail,
//     DashBoard,
//     NavMenu
//   }
}
</script>
