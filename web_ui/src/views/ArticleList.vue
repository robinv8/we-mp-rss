<template>
  <a-spin :loading="fullLoading" tip="正在刷新..." size="large">
  <a-layout class="article-list">
    <a-layout-sider :width=300
      :style="{ background: '#fff', padding: '0', borderRight: '1px solid #eee', display: 'flex', flexDirection: 'column' ,border:0}">
      <a-card :bordered="false" title="公众号" 
        :headStyle="{ padding: '12px 16px', borderBottom: '1px solid #eee', background: '#fff', zIndex: 1 ,border:0}">
        <template #extra>
          <a-button type="primary" @click="showAddModal">
            <template #icon><icon-plus /></template>
            添加订阅
          </a-button>
        </template>
        <div style="display: flex; flex-direction: column;; background: #fff">
            <a-list :data="mpList" :loading="mpLoading" bordered>
              <template #item="{ item, index }">
                <a-list-item @click="handleMpClick(item.id)" :class="{ 'active-mp': activeMpId === item.id }"
                  style="padding: 9px 8px; cursor: pointer; display: flex; align-items: center; justify-content: space-between;">
                 <div style="display: flex; align-items: center;">
                   <img :src="Avatar(item.avatar)" width="40" style="float:left;margin-right:1rem;"/>
                   <a-typography-text  strong style="line-height:32px;">
                     {{ item.name || item.mp_name }}
                   </a-typography-text>
                   <a-button v-if="activeMpId === item.id && item.id!=''" size="mini" type="text" status="danger" @click="$event.stopPropagation(); deleteMp(item.id)" >
                     <template #icon><icon-delete /></template>
                    </a-button>
                  </div>
                </a-list-item>
              </template>
            </a-list>
            <a-pagination :total="mpPagination.total" simple  @change="handleMpPageChange" :show-total="true" style="margin-top: 1rem;"/>
        </div>
      </a-card>
    </a-layout-sider>

    <a-layout-content :style="{ padding: '20px', width: '100%'}" >
      <a-page-header 
      :title="activeFeed ? activeFeed.name : '全部'" 
      :subtitle="'管理您的公众号订阅内容'" :show-back="false">
          <template #extra>
          <a-space>
            <a-button @click="refresh" v-if="activeFeed?.id!=''">
              <template #icon><icon-refresh /></template>
              刷新
            </a-button>
            <a-button @click="clear_articles" v-else>
              <template #icon><icon-delete /></template>
              清理无效文章
            </a-button>
            <a-button @click="handleAuthClick">
              <template #icon><icon-scan /></template>
              刷新授权
            </a-button>
            <a-dropdown>
              <a-button>
                <template #icon><IconWifi /></template>
                订阅
                <icon-down />
              </a-button>
              <template #content>
                <a-doption @click="rssFormat='atom'; openRssFeed()">ATOM</a-doption>
                <a-doption @click="rssFormat='rss'; openRssFeed()">RSS</a-doption>
                <a-doption @click="rssFormat='json'; openRssFeed()">JSON</a-doption>
                <a-doption @click="rssFormat='md'; openRssFeed()">Markdown</a-doption>
                <a-doption @click="rssFormat='txt'; openRssFeed()">Text</a-doption>
              </template>
            </a-dropdown>
            <!-- <a-button @click="importArticles" tooltip="导入JSON格式文章数据">
              <template #icon><icon-import /></template>
              导入
            </a-button>
            <a-button @click="exportArticles" tooltip="导出当前文章列表为JSON文件">
              <template #icon><icon-export /></template>
              导出
            </a-button> -->
            <a-button type="primary" status="danger" @click="handleBatchDelete" :disabled="!selectedRowKeys.length">
              <template #icon><icon-delete /></template>
              批量删除
            </a-button>
          </a-space>
        </template>
      </a-page-header>

      <a-modal 
        v-model:visible="refreshModalVisible" 
        title="设置刷新范围"
        @ok="handleRefresh"
        @cancel="refreshModalVisible = false"
      >
        <a-form :model="refreshForm" :rules="refreshRules">
          <a-form-item field="startPage" label="开始页码">
            <a-input-number v-model="refreshForm.startPage" :min="1" />
          </a-form-item>
          <a-form-item field="endPage" label="结束页码">
            <a-input-number v-model="refreshForm.endPage" :min="refreshForm.startPage" />
          </a-form-item>
        </a-form>
      </a-modal>

      <a-card style="border:0">
        <a-alert type="success" closable>{{activeFeed?.mp_intro||"请选择一个公众号码进行管理,搜索文章后再点击订阅会有惊喜哟！！！"}}</a-alert>
        <div class="search-bar">
          <a-input-search v-model="searchText" placeholder="搜索文章标题" @search="handleSearch" @keyup.enter="handleSearch" allow-clear />
        </div>

        <a-table :columns="columns" :data="articles" :loading="loading" :pagination="pagination" style="width: 100%"
          @page-change="handlePageChange"  row-key="id"
          :row-selection="{
            type: 'checkbox',
            showCheckedAll: true,
            width: 50,
            fixed: true
          }"
          v-model:selectedKeys="selectedRowKeys">
          <template #status="{ record }">
            <a-tag :color="statusColorMap[record.status]">
              {{ statusTextMap[record.status] }}
            </a-tag>
          </template>
          <template #actions="{ record }">
            <a-space>
              <a-button type="text" @click="viewArticle(record)">
                <template #icon><icon-eye /></template>
              </a-button>
              <a-button type="text" status="danger" @click="deleteArticle(record.id)">
                <template #icon><icon-delete /></template>
              </a-button>
            </a-space>
          </template>
        </a-table>

        <a-modal 
          v-model:visible="articleModalVisible" 
          :title="currentArticle.title"
          width="800px"
          :footer="false"
        >
          <div style="padding: 20px; max-height: 70vh; overflow-y: auto">
            <div v-html="currentArticle.content"></div>
            <div style="margin-top: 20px; color: var(--color-text-3); text-align: right">
              {{ currentArticle.time }}
            </div>
          </div>
        </a-modal>
      </a-card>
    </a-layout-content>
  </a-layout>
</a-spin>
</template>

<script setup lang="ts">
import { Avatar } from '@/utils/constants'
import { ref, onMounted, h } from 'vue'
import axios from 'axios'
import { IconApps, IconAtt, IconDelete, IconEdit, IconEye, IconRefresh, IconScan, IconWeiboCircleFill, IconWifi } from '@arco-design/web-vue/es/icon'
import { getArticles,deleteArticle as deleteArticleApi ,ClearArticle } from '@/api/article'
import { getSubscriptions, UpdateMps} from '@/api/subscription'
import { inject } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { formatDateTime,formatTimestamp } from '@/utils/date'
import router from '@/router'
import {  deleteMpApi } from '@/api/subscription'

const articles = ref([])
const loading = ref(false)
const mpList = ref([])
const mpLoading = ref(false)
const activeMpId = ref('')
const selectedRowKeys = ref([])
const mpPagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showPageSize: false,
  showJumper: false,
  showTotal: true,
  pageSizeOptions: [5, 10, 15]
})
const searchText = ref('')
const filterStatus = ref('')

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true,
  showJumper: true,
  showPageSize: true,
  pageSizeOptions: [10]
})

const statusTextMap = {
  published: '已发布',
  draft: '草稿',
  deleted: '已删除'
}

const statusColorMap = {
  published: 'green',
  draft: 'orange',
  deleted: 'red'
}

const columns = [
  {
    title: '文章标题',
    dataIndex: 'title',
    width: '60%',
    ellipsis: true,
    render: ({ record }) => h('a', {
      href: record.url || '#',
      title: record.title,
      target: '_blank',
      style: { color: 'var(--color-text-1)' }
    }, record.title)
  },
  {
    title: '公众号',
    dataIndex: 'mp_id',
    width: '8%',
    ellipsis: true,
    render: ({ record }) => {
      const mp = mpList.value.find(item => item.id === record.mp_id);
      return h('span', {
        style: { color: 'var(--color-text-3)' }
      }, record.mp_name||mp?.name || record.mp_id)
    }
  },
  {
    title: '更新时间',
    dataIndex: 'created_at',
    width: '8%',
    render: ({ record }) => h('span',
      { style: { color: 'var(--color-text-3)', fontSize: '12px' } },
      formatDateTime(record.created_at)
    )
  },
  {
    title: '发布时间',
    dataIndex: 'publish_time',
    width: '8%',
    render: ({ record }) => h('span',
      { style: { color: 'var(--color-text-3)', fontSize: '12px' } },
      formatTimestamp(record.publish_time)
    )
  },
  {
    title: '正文',
    width: '8%',
    render: ({ record }) => h('span', 
      { style: { color: 'var(--color-text-3)', fontSize: '12px' } },
      record.content && record.content.trim() ? '是' : '否'
    )
  },
  {
    title: '操作',
    dataIndex: 'actions',
    slotName: 'actions'
  }
]

const handleMpPageChange = (page: number, pageSize: number) => {
  mpPagination.value.current = page
  mpPagination.value.pageSize = pageSize
  fetchMpList()
}
const rssFormat = ref('atom')
const activeFeed=ref({
  id:"",
  name:"全部",
})
const handleMpClick = (mpId: string) => {
  activeMpId.value = mpId
  pagination.value.current = 1
  activeFeed.value=mpList.value.find(item => item.id === activeMpId.value)
  console.log(activeFeed.value)

  fetchArticles()
}

const fetchArticles = async () => {
  loading.value = true
  try {
    console.log('请求参数:', {
      page: pagination.value.current - 1,
      pageSize: pagination.value.pageSize,
      search: searchText.value,
      status: filterStatus.value,
      mp_id: activeMpId.value
    })

    const res = await getArticles({
      page: pagination.value.current - 1,
      pageSize: pagination.value.pageSize,
      search: searchText.value,
      status: filterStatus.value,
      mp_id: activeMpId.value
    })

    // 确保数据包含必要字段
    articles.value = (res.list || []).map(item => ({
      ...item,
      mp_name: item.mp_name || item.account_name || '未知公众号',
      publish_time: item.publish_time || item.create_time || '-',
      url: item.url||"https://mp.weixin.qq.com/s/" + item.id
    }))
    pagination.value.total = res.total || 0
  } catch (error) {
    console.error('获取文章列表错误:', error)
    Message.error(error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number, pageSize: number, type?: string) => {
  console.log('分页事件触发:', {page, pageSize, type})
  pagination.value.current = page
  pagination.value.pageSize = pageSize
  fetchArticles()
}

const handleSearch = () => {
  pagination.value.current = 1
  fetchArticles()
}

const wechatAuthQrcodeRef = ref()
  const showAuthQrcode = inject('showAuthQrcode') as () => void
  const handleAuthClick = () => {
    showAuthQrcode()
  }

const openRssFeed = () => {
  const format = ['rss', 'atom', 'json','md','txt'].includes(rssFormat.value) 
    ? rssFormat.value 
    : 'atom'
  let search=""
  if(searchText.value!=""){
    search="/search/"+searchText.value;
  }
  if (!activeMpId.value) {
    window.open(`/feed${search}/all.${format}`, '_blank')
    return
  }
  const activeMp = mpList.value.find(item => item.id === activeMpId.value)
  if (activeMp) {
    window.open(`/feed${search}/${activeMpId.value}.${format}`, '_blank')
  }
}

const fullLoading = ref(false)

const refreshModalVisible = ref(false)
const refreshForm = ref({
  startPage: 0,
  endPage: 1
})
const refreshRules = {
  startPage: [{ required: true, message: '请输入开始页码' }],
  endPage: [{ required: true, message: '请输入结束页码' }]
}

const showRefreshModal = () => {
  refreshModalVisible.value = true
}

const handleRefresh = () => {
  fullLoading.value = true
  UpdateMps(activeMpId.value, {
    start_page: refreshForm.value.startPage,
    end_page: refreshForm.value.endPage
  }).then(() => {
    Message.success('刷新成功')
    refreshModalVisible.value = false
  }).finally(() => {
    fullLoading.value = false
  })
  fetchArticles()
}
const clear_articles = () => {
  fullLoading.value = true
  ClearArticle().then((res) => {
    Message.success(res?.message||'清理成功')
    refreshModalVisible.value = false
  }).finally(() => {
    fullLoading.value = false
  })
  fetchArticles()
}

const refresh = () => {
  showRefreshModal()
}

const showAddModal = () => {
  router.push('/add-subscription')
}

const handleAddSuccess = () => {
  fetchArticles()
}

const viewArticle = (record: any) => {
  if (record.content) {
    // 处理图片链接，在所有图片链接前加上/static/res/logo/
    const processedContent = record.content.replace(
      /(<img[^>]*src=["'])(?!\/static\/res\/logo\/)([^"']*)/g,
      '$1/static/res/logo/$2'
    )
    currentArticle.value = {
      title: record.title,
      content: processedContent,
      time: formatDateTime(record.created_at)
    }
    articleModalVisible.value = true
  } else {
    window.open(record.url, '_blank')
  }
}

const currentArticle = ref({
  title: '',
  content: '',
  time: ''
})
const articleModalVisible = ref(false)

const deleteArticle = (id: number) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除该文章吗？删除后将无法恢复。',
    okText: '确认',
    cancelText: '取消',
    onOk: async () => {
      await deleteArticleApi(id);
      Message.success('删除成功');
      fetchArticles();
    },
    onCancel: () => {
      Message.info('已取消删除操作');
    }
  });
}

const handleBatchDelete = () => {
  Modal.confirm({
    title: '确认批量删除',
    content: `确定要删除选中的${selectedRowKeys.value.length}篇文章吗？删除后将无法恢复。`,
    okText: '确认',
    cancelText: '取消',
    onOk: async () => {
      try {
        await Promise.all(selectedRowKeys.value.map(id => deleteArticleApi(id)));
        Message.success(`成功删除${selectedRowKeys.value.length}篇文章`);
        selectedRowKeys.value = [];
        fetchArticles();
      } catch (error) {
        Message.error('删除部分文章失败');
      }
    },
    onCancel: () => {
      Message.info('已取消批量删除操作');
    }
  });
}

onMounted(() => {
  console.log('组件挂载，开始获取数据')
  fetchMpList().then(() => {
    console.log('公众号列表获取完成')
    fetchArticles()
  }).catch(err => {
    console.error('初始化失败:', err)
  })
})

const fetchMpList = async () => {
  mpLoading.value = true
  try {
    const res = await getSubscriptions({
      page: mpPagination.value.current - 1,
      pageSize: mpPagination.value.pageSize
    })
    
    mpList.value = res.list.map(item => ({
      id: item.id || item.mp_id,
      name: item.name || item.mp_name,
      avatar: item.avatar || item.mp_cover || '',
      mp_intro: item.mp_intro || item.mp_intro || '',
      article_count: item.article_count || 0
    }))
    // 添加'全部'选项
    mpList.value.unshift({
      id: '',
      name: '全部',
      avatar: '/static/logo.svg',
      mp_intro: '显示所有公众号文章',
      article_count: res.total || 0
    });
    mpPagination.value.total = res.total || 0
  } catch (error) {
    console.error('获取公众号列表错误:', error)
  } finally {
    mpLoading.value = false
  }
}
const deleteMp = async (mpId: string) => {
  try {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除该订阅号吗？删除后将无法恢复。',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        await deleteMpApi(mpId);
        Message.success('订阅号删除成功');
        fetchMpList();
      },
      onCancel: () => {
        Message.info('已取消删除操作');
      }
    });
  } catch (error) {
    console.error('删除订阅号失败:', error);
    Message.error('删除订阅号失败，请稍后重试');
  }
}

const importArticles = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (!file) return;

    try {
      const content = await file.text();
      const data = JSON.parse(content);
      // 这里应该调用API导入数据
      Message.success(`成功导入${data.length}篇文章`);
    } catch (error) {
      console.error('导入文章失败:', error);
      Message.error('导入失败，请检查文件格式');
    }
  };
  input.click();
};

const exportArticles = () => {
  if (!articles.value.length) {
    Message.warning('没有文章可导出');
    return;
  }

  const data = JSON.stringify(articles.value, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `articles_${activeMpId.value || 'all'}_${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  Message.success('导出成功');
};
</script>

<style scoped>
.article-list {
  /* height: calc(100vh - 186px); */
}

.a-layout-sider {
  overflow: hidden;
}

.a-list-item {
  cursor: pointer;
  padding: 12px 16px;
  transition: all 0.2s;
  margin-bottom:0 !important;
}

.a-list-item:hover {
  background-color: var(--color-fill-2);
}

.active-mp {
  background-color: var(--color-primary-light-1);
}

.search-bar {
  display: flex;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .a-layout-sider {
    width: 100% !important;
    max-width: 100%;
  }

  .a-layout {
    flex-direction: column;
  }
}
</style>