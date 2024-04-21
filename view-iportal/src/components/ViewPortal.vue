<template>
    <div>
  
      <el-row :gutter="20" v-for="(list, index) in listData" :key="index" type="flex" class="row-view-item">
        <el-col :span="1">
          <el-tag :style="{ backgroundColor: list.color }">{{ list.view_name }}</el-tag>
        </el-col>
        <el-col :span="4" v-for="(view, index) in list.viewData" :key="index">
          <ViewCard :view="view" :bgcolor="list.color"></ViewCard>
        </el-col>
      </el-row>
    </div>
  
  </template>
  
  <script>
  
  import ViewCard from './ViewCard.vue'
  
  export default {
    name: 'VIEW-PORTAL',
    components: {
        ViewCard
    },
    data() {
      return {
        listData: [],
      }
    },
  
  
    created() {
      this.initData()
    },
    computed: {
  
    },
    methods: {
      // 初始化数据
      initData() {
        const Mock = require('mockjs')
        let apiData = Mock.mock({
          'data|10': [{
            'id|+1': 1,
            'view_name|1': '@cword(1, 3)' + '应用视角',
            'view_type|1': ['user', 'performance', 'deployment'],
            'color|1': ['#67C23A', '#E6A23C', '#F56C6C', '#909399'],
            'viewData|1-10': [
              { 'area': '@cword(1,3)' + '领域', 'count': '@integer(1, 100)', 'applicationsData|1-15': [{ 'system_id': '@id()', 'system_name': '@cword(3,6)', 'error_count': '@integer(0, 2)' }] }
            ]
          }]
        })
        this.listData = apiData.data
        console.log(this.listData)
      },

    }
  }
  </script>
  <style scoped>
  /*每行的内边距*/
  .row-view-item {
    padding: 10px;
  }

  .el-tag {
      writing-mode: vertical-lr;
      text-orientation: upright;
      font-size: 15px;
      color: white;
      display: flex;
      justify-content: center; /*垂直居中*/
      align-items: center; /*水平居中*/
      width: 100%;
      height: 350px;
}

  </style>