<template>
    <div>

        <h1>aaaa</h1>

        <div id="graph_id">
        </div>
        <el-dialog title="提示" :visible.sync="dialogVisible" width="30%" :before-close="handleClose">
            <span>这是一段信息</span>
            <span slot="footer" class="dialog-footer">
                <el-button @click="dialogVisible = false">取 消</el-button>
                <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
import { Graph, Path, Cell } from '@antv/x6'
import Mock from 'mockjs'
import { data } from './data'
export default {
    components: {
    },
    data() {
        return {
            pipelineData: data,
            dialogVisible: false


        };
    },
    mounted() {
        this.initGraph();
    },
    created() {

    },
    methods: {


        initGraph() {

            Graph.registerNode('pipeline-node', {
                inherit: 'rect',
                width: 100,
                height: 40,
            })

            const graph = new Graph({
                container: document.getElementById('graph_id'),
                with: 1000,
                height: 1000,
                interacting: false

            });

            console.log(this.pipelineData)

            graph.fromJSON(this.pipelineData)
            graph.on('node:click', ({ e, x, y, node, view }) => {

                console.log(e, x, y, node, view)
                this.dialogVisible = true
            })
        },
    },
};
</script>

<style scoped>
.tag {
    width: 180px;
    height: 20px;
    margin-right: 10px;
    display: inline-block;
}
</style>