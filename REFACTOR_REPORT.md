# UniPulse 架构重构 - 优化报告

## 日期：2026-05-07

## 重构目标
将单体 1087 行 index.html 拆分为 8 个模块化文件，修复所有点评中提到的工程问题。

## 新的文件结构
```
unipulse/
├── index.html         (128行, 只留骨架 + script引用)
├── css/
│   └── style.css      (508行, 独立样式表)
├── js/
│   ├── data.js        (320行, 数据层 - universities/programs/forumPosts/I18N)
│   ├── state.js       (90行, 状态管理 - pub/sub + 原子操作)
│   ├── router.js      (48行, Hash路由 - #/rankings/3)
│   ├── render.js      (280行, 渲染 - DocumentFragment + 语义化标签)
│   ├── compare.js     (130行, 对比模块 - 高亮最佳/最差)
│   └── main.js        (152行, 初始化 + 事件绑定 + 汉堡菜单)
└── SPEC.md
```

## 修复清单（对照点评）

### Phase 1 - 止血 ✅
| 问题 | 修复 |
|------|------|
| 移动端导航消失 | 添加汉堡菜单 + 动态渲染移动端菜单列表 |
| 搜索无防抖 | 300ms debounce（State.setSearch） |
| 模态框滚动穿透 | 打开时 body.scroll-locked → overflow:hidden |
| 缺少 ARIA | 全站添加 role/tabindex/aria-label/aria-live |
| transition:all | 全部改为明确属性（transform, box-shadow, color等）|
| 无 reduced-motion | @media(prefers-reduced-motion) 覆盖所有动画 |
| 键盘不可用 | 所有卡片/行添加 tabindex + keydown(Enter/Space) |

### Phase 2 - 解耦 ✅
| 问题 | 修复 |
|------|------|
| 单体巨石 | 拆为8个文件，数据/状态/路由/渲染/交互分离 |
| URL路由缺失 | Hash路由 #/rankings/3 → 可分享链接 |
| 硬编码状态 | 集中 State 模块，pub/sub 响应式通知 |
| 预渲染浪费 | 页面懒加载 - 仅首次切换时调用 render |
| 标签颜色脆弱 | 标签改为 {text, type} 结构，确保语义一致性 |
| 搜索+筛选冲突 | 添加"无结果"提示 + 一键清空筛选 |

### Phase 3 增强 ✅
| 问题 | 修复 |
|------|------|
| 对比不突出差异 | 新增 compare-table 高亮每行最高分(👑绿色)和最低分(红色) |
| null值处理 | 索邦大学就业/首尔大学关怀设为 null，显示"暂无数据" |
| 评分缺乏解释 | 排名页添加"查看评分方法论"按钮 |
| 论坛纯假象 | 帖子标题改为 button 元素，语义化交互 |
| DOM 直接替换 | 使用 DocumentFragment 构建卡片，提升性能 |
| 论坛帖子按钮 | 使用<button>而非<div onclick> |

## 关键技术决策
1. 放弃框架引入（React/Vue会增大体积），用模块化 vanilla JS
2. 选择 Hash 路由而非 History API（兼容 file:// 和任意静态服务器）
3. 全局 script 标签加载（ES modules 在 file:// 下有 CORS 限制）
4. State 使用简单 pub/sub 而非 Proxy（兼容性更好，代码更明晰）
