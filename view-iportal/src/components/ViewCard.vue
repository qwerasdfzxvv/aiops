<template>
    <div >
        <el-badge :value="view.count" class="badge-top">
            <el-card :body-style="{ padding: '5px' }" >
                <div slot="header">
                    <p class="card-title" > {{ view.area }}</p>
                </div>
                <div>
                    <el-tooltip placement="right" v-for="(application, index) in view.applicationsData.slice(0, 5)"
                        :key="index">
                        <div slot="content">
                            <div>
                                <p>{{ application.system_name }}</p>
                                <p>{{ application.error_count }}</p>
                            </div>
                        </div>
                        <div class="card-content" >
                            <el-badge :value="application.error_count" :hidden="application.error_count == 0">
                                <el-tag size="mmedium" @click="handleTagClick(application)" >{{
                                    application.system_name }}</el-tag>
                            </el-badge>
                        </div>
                    </el-tooltip>

                    <el-popover placement="top" trigger="hover" v-if="view.applicationsData.length > 5"
                        ref="viewpopover">
                        <el-tooltip placement="right" v-for="(application, index) in view.applicationsData"
                            :key="index">
                            <div slot="content">
                                <div>
                                    <p>{{ application.system_name }}</p>
                                    <p>{{ application.error_count }}</p>
                                </div>
                            </div>
                            <div class="card-content">
                                <el-badge :value="application.error_count" :hidden="application.error_count == 0">
                                    <el-tag size="mmedium" @click="handleTagClick(application)">{{
                                        application.system_name }}</el-tag>
                                </el-badge>
                            </div>
                        </el-tooltip>
                        <div class="card-content" slot="reference">
                            <el-tag>..更多</el-tag>
                        </div>
                    </el-popover>


                </div>
            </el-card>
        </el-badge>

        <el-drawer :title="drawerTitle" :visible.sync="drawerVisible" @open="handleDrawerOpen"
            @close="handleDrawerClose" size="50%">
            <el-table :data="targetData" style="width: 100%" height="250">
                <el-table-column fixed prop="systemId" label="系统编号" width="150">
                </el-table-column>
                <el-table-column prop="systemName" label="系统名称" width="120">
                </el-table-column>
                <el-table-column prop="region" label="机房" width="120">
                </el-table-column>
                <el-table-column prop="target" label="指标名称" width="120">
                </el-table-column>
                <el-table-column prop="status" label="状态" width="300">
                    <template slot-scope="scope">
                        <el-tag :type="scope.row.status == 0 ? 'danger' : 'success'" effect="dark" size="medium">{{
                            scope.row.status == 0 ? '异常' : '正常' }}</el-tag>
                    </template>
                </el-table-column>
            </el-table>
            <hr>
            <!-- <v-chart class="chart" :option="option" autoresize /> -->
        </el-drawer>

    </div>
</template>

<script>
// import { backgroundColor } from 'echarts/lib/theme/dark'

// import ECharts from 'vue-echarts'
// import 'echarts/lib/chart/line'       //绘制不同的图表要引入不同的chart和component
// import 'echarts/lib/component/polar'


export default {
    name: 'VIEW-CARD',
    components: {
        // 'v-chart': ECharts
    },

    props: {
        view: {
            type: Object,
            default: () => {
                return {}
            }
        },
        bgcolor: {
            type: String,
            default: () => {
                return "#67C23A"
            }
        }
    },
    mounted() {
        if (this.$refs.viewpopover) {
            this.$refs.viewpopover.$refs.popper.style.backgroundColor = this.bgcolor
        }
    },
    data() {
        // console.log(this.view)
        console.log(this.bgcolor)
        return {
          
            custombackgroundColor:"#67C23A",
            showDrawer: false,
            // 抽屉的标题
            drawerTitle: '',
            // 抽屉的显示状态
            drawerVisible: false,
      
            // 指标数据
            targetData: [],
            option: {
                title: {
                    text: 'Traffic Sources',
                    left: 'center',
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b} : {c} ({d}%)',
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: ['Direct', 'Email', 'Ad Networks', 'Video Ads', 'Search Engines'],
                },
                series: [
                    {
                        name: 'Traffic Sources',
                        type: 'pie',
                        radius: '55%',
                        center: ['50%', '60%'],
                        data: [
                            { value: 335, name: 'Direct' },
                            { value: 310, name: 'Email' },
                            { value: 234, name: 'Ad Networks' },
                            { value: 135, name: 'Video Ads' },
                            { value: 1548, name: 'Search Engines' },
                        ],
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)',
                            },
                        },
                    },
                ],
            }
        }
    },
    watch: {
        showDrawer(newVal, oldVal) {
            console.log(newVal, oldVal)
            this.drawerVisible = newVal;
        },
       
    },
    computed: {
   
   },
   
    methods: {
        handleTagClick(application) {
            console.log(application)
            this.drawerTitle = application.system_name
            this.showDrawer = true
            // this.$emit('handleTagClick', id)
        },
        handleDrawerOpen() {
            const Mock = require('mockjs')
            let apiData = Mock.mock({
                'data|10': [{
                    'systemId': '@id()',
                    'systemName|1': '@cword(1, 3)' + '系统',
                    'region|1': '@cword(1, 3)' + '机房',
                    'target|1': '@cword(1, 3)' + '指标',
                    'status|1': [0, 1]
                }]
            })
            this.targetData = apiData.data
            console.log(this.targetData)
        },
        handleDrawerClose() {
            console.log('handleDrawerClose')
            //清理drawer的相关数据
            this.showDrawer = false
            this.drawerVisible = false
            this.targetData = []

        }
    }
}
</script>

<style scoped>

.card-title {
    border-left: 3px solid v-bind(bgcolor);
    border-bottom: 0.5px solid v-bind(bgcolor);
    padding-bottom: 5px;
    box-sizing: border-box;
    width: 100%;
    font-size: 14px;
    background: #fff;
    border-radius: 4px;
}



.badge-top {

    /*仅对第一个生效*/
    >.el-badge__content {
        background-color: v-bind(bgcolor);
    }
}

.el-card__body, .card-content{
    display: flex;
    align-items: center;
    justify-content: center;

}



.el-tag {
    font-size: 15px;
    margin-bottom: 10px;
    width: 150px;
    color: azure;
    background-color: v-bind(bgcolor);
    text-align: center;
    /* 文件居中 */
}


.el-card {
    width: 200px;
    height: 350px;
    border-color: v-bind(bgcolor);
    border-width: 2px;
}

.el-card__header {
    padding-left: 10px;
}
</style>