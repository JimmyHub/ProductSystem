import Vue from 'vue'
import Router from 'vue-router'
import history from '@/components/new/history.vue'

Vue.use(Router)

export default new Router({
     routes:[
        {
          name:'index',
          path:'/index',
          component:history
        }
        ]
})