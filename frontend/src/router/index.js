import Vue from 'vue'
import Router from 'vue-router'
import history from '@/components/new/history.vue'

Vue.use(Router)

export default new Router({
     routes:[
        // 總表
        { 
          name:'index',
          path:'/index',
          component:history
        },
        // 歷史表
        // { 
        //   name:'history',
        //   path:'/history',
        //   component:history
        // }

        ]
})