<template>
  <el-table
    :data="tableData"
    style="width: 100%">
    <el-table-column type="expand">
      <template slot-scope="props">
        <el-form label-position="left" inline class="demo-table-expand">
          <el-form-item label="Request">
            <pre v-highlightjs><code class="html">{{props.row.vul_url}}</code></pre>
            <!-- <span>{{ props.row.vul_url }}</span> -->
          </el-form-item>
          <el-form-item label="Response">
            <!-- <div style="white-space: pre-line">{{ props.row.vul_response }}</div> -->
            <pre v-highlightjs><code class="html">{{props.row.vul_response}}</code></pre>
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
</template>

<style>
  .demo-table-expand {
    font-size: 0;
  }
  .demo-table-expand label {
    width: 90px;
    color: #99a9bf;
  }
  .demo-table-expand .el-form-item {
    margin-right: 0;
    margin-bottom: 0;
    width: 50%;
  }
</style>

<script>
// import axios from 'axios'
// import {dashboard} from '@/api/api'
export default {
  props: {
    tableData: {
      type: Array,
      default: function () {
        return []
      }
    }
  },
  data () {
    return {
      // c: null
    }
  },
  mounted () {
  },
  updated () {
  }
}
</script>
