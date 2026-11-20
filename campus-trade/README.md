# 校园智能二手交易平台（Campus Trade）

毕业设计项目 · 广州工程技术职业学院 · CY 类（软件工程 / 模拟课题）
题目：**基于 SpringBoot 的校园智能二手交易平台设计与实现**

---

## 一、技术栈

| 层次 | 选型 |
| --- | --- |
| 后端 | JDK 17、SpringBoot 3.2.5、MyBatis-Plus 3.5.7、jjwt 0.11.5、Spring Security Crypto（BCrypt） |
| 前端 | Vue 3、Vite、Element Plus、Axios、Vue Router（history 模式） |
| 数据库 | MySQL 8.0，库名 `campus_trade` |
| AI | 智谱 GLM-4-Flash（OpenAI 协议兼容，Function Calling） |

## 二、目录结构

```
1/
├─ campus-trade-backend/     SpringBoot 后端（端口 8080）
├─ campus-trade-frontend/    Vue3 前端（端口 5173）
└─ sql/
   ├─ schema.sql             初始建表脚本
   ├─ schema_v2.sql          全新建库脚本（V2，带测试数据）
   └─ upgrade_v2.sql         增量升级脚本（V1 → V2，不丢数据）
```

## 三、启动步骤

### 1. 数据库

在项目根目录（`README.md` 所在目录）执行，路径均为相对路径，换电脑也能用：

```sql
-- 全新环境执行 schema_v2.sql（已含订单快照字段）
source ./sql/schema_v2.sql;
-- 已有 V2 旧库：先跑增量升级补订单快照字段
-- source ./sql/upgrade_v3.sql;
```

测试账号（密码均为 `123456`）：

| 用户名 | 角色 | 说明 |
| --- | --- | --- |
| admin | 管理员 | 可进管理后台 |
| stu001 | 学生 | 可发布商品、下单 |

### 2. 后端

IDEA 中刷新 Maven 后运行 `CampusTradeApplication`，或命令行：

```powershell
cd campus-trade-backend
mvn spring-boot:run
```

健康检查：`GET http://localhost:8080/api/goods/page`

### 3. 前端

```powershell
cd campus-trade-frontend
npm install
npm.cmd run dev
```

访问 http://localhost:5173

> PowerShell 禁止运行 ps1 脚本时，用 `npm.cmd` 而不是 `npm`。

### 4. 环境变量（可选，安全相关）

敏感配置已改为环境变量注入，不写死在 `application.yml`。本地不设置也能跑（用开发默认值），但**上交/答辩前建议设置**：

| 环境变量 | 用途 | 不设置时的默认 |
| --- | --- | --- |
| `AI_API_KEY` | 智谱大模型 Key | 空（AI 自动降级为本地检索） |
| `DB_PASSWORD` | MySQL 密码 | `123456` |
| `DB_USERNAME` | MySQL 用户名 | `root` |
| `JWT_SECRET` | JWT 签名密钥（≥32 字节） | 内置开发用默认值 |
| `CORS_ALLOWED_ORIGINS` | 允许跨域的来源，逗号分隔 | 仅本机 `localhost` / `127.0.0.1` |

手机或另一台电脑要访问后端时，用 `CORS_ALLOWED_ORIGINS=http://localhost:[*],http://192.168.1.10:5173` 显式加具体源，不要改回放行整个内网段。

## 四、功能清单

| 模块 | 接口 | 说明 |
| --- | --- | --- |
| 认证 | `POST /api/user/register`、`POST /api/user/login` | JWT，密码 BCrypt 存储 |
| 商品浏览 | `GET /api/goods/page`、`GET /api/goods/{id}` | 详情自动累加浏览量 |
| 商品发布 | `POST /api/goods`、`PUT /api/goods/{id}`、`DELETE /api/goods/{id}` | 归属校验，只能改自己的 |
| 我的发布 | `GET /api/goods/my`、`PUT /api/goods/{id}/status` | 上架 / 下架 |
| 图片上传 | `POST /api/file/upload` | 5MB 限制、UUID 重命名、防路径穿越 |
| 订单 | `POST /api/orders`、`GET /api/orders/my`、`PUT /api/orders/{id}/pay|finish|cancel` | 状态机 0 待付款 → 1 已付款 → 2 已完成 / 3 已取消 |
| 管理端 | `/api/admin/stats|users|goods|orders` | `@AdminOnly` 注解 + 拦截器校验 role=1 |
| AI 导购（智能体） | `POST /api/ai/chat` | 多轮对话 + Function Calling：模型解析条件 → 后端查库 → 模型组织语言，最多 4 轮工具调用 |
| AI 写描述 | `POST /api/ai/generate-desc` | 发布页"AI 帮我写描述"按钮 |

## 五、几个关键设计（答辩要点）

1. **并发下的商品锁定**：下单不是「先查状态再改」，而是一条条件更新
   `UPDATE goods SET status=2 WHERE id=? AND status=1`，返回 0 行说明被别人抢先了。
   这样在数据库层面天然避免超卖，不需要分布式锁。

2. **订单状态机**：0 待付款 → 1 已付款 → 2 已完成；0 → 3 已取消。
   所有状态变更都是条件更新（`WHERE status = 期望值`），杜绝重复付款、重复收货。

3. **超时自动取消**：`OrderTimeoutTask` 每 5 分钟扫一次，未付款超过 120 分钟自动取消并释放商品，
   避免商品被不付款的人长期锁死。

4. **AI 防幻觉**：不让大模型直接生成商品，而是用 Function Calling 让模型输出查询条件
   （关键词 / 分类 / 价格区间），后端查真实数据后再回填给模型组织语言。
   没配 API Key 或接口超时会自动降级为本地关键词检索，页面不会报错。
   另加两道代码级兜底：① 模型回复里出现的价格和成色会和工具查到的数据逐条比对，
   对不上（比如把 180 元说成 300 元、把七成新说成八成新）就整段换成由数据库字段拼出的摘要；
   ② 回复命中 `searchGoods`、`tool_calls`、模型名、接口地址等关键词时直接换成固定话术，
   防止提示词注入把工具定义套出来。
   ③ 工具检索做了**多级召回**，不靠一整串 `LIKE`：库里叫"高等数学 第七版 上下册"，
   用户说"高等数学真题"时先把修饰词削掉（真题/试卷/教材/二手/有没有…），
   再按别名展开（高数↔高等数学、英语四级→英语、山地车↔自行车），
   还查不到就去掉模型猜的分类、最后拆成多词 OR 兜底；命中即返回，全落空才算没有。
   （`tools/RecallDbTest.java` 就是拿真实 MySQL 跑这些问法的验证脚本）
   ④ **零召回不许自由发挥**：只要模型调用过工具却一条都没查到，回复直接换成固定话术
   （"站内现在没有符合条件的在售商品……"），模型没有数据就不给它编的机会；
   即使查到了商品，只要回复里出现书名号 `《》` 或顿号（说明它在列举商品名），也整段换成
   由数据库字段拼出的摘要——"有高等数学、线性代数、概率论"这种列表，名字无法逐条核对，
   干脆不让模型来写。另外模型**没调工具却宣称"经过搜索/找到了一本"或报了价格**，
   同样判为编造、换成固定话术。
   ⑤ 用户只说"有没有书 / 有没有教材"这类泛词时，因为标题里没有"书"字，会自动转成
   `category=教材` 查询，而不是拿"书"去 `LIKE` 标题。
   ⑥ **规格词归一**：`第九代` → `第9代`；因为库里标题是 `iPad 第 9 代 64G WiFi 版`（带空格），
   查询时额外用 `REPLACE(title,' ','')` 再比一次，所以"第9代""第 9 代""第九代""64G"都能命中；
   `第/代/版/款` 这类单字虚词直接丢弃，避免"有没有版"这种问法把整张表捞出来。
   ⑦ **模型偷懒兜底**：如果这一轮模型压根没调工具（多轮里想凭上下文回忆），
   后端会拿用户最后一句自己检索一次，命中就直接返回真实商品 + 数据库摘要，
   不让"没查库却报数据"的回答走到前端；如果后端也查不到、而用户确实在问"有没有货/多少钱"，
   就直接回固定话术，**不让模型拿"华为、小米、苹果"这种凭空的品牌清单糊弄**。
   品类别名也进了同义词表（`平板/平板电脑 ↔ iPad`、`山地车 ↔ 自行车`、`耳机 ↔ 蓝牙耳机` 等），
   因为库里标题写的是 `iPad 第 9 代`，压根没有"平板"两个字。

5. **密码安全**：BCrypt 加盐哈希；老库里的明文密码在下次登录成功时自动升级为密文（渐进式迁移）。

6. **统一异常处理**：`GlobalExceptionHandler` 区分业务异常 / 参数校验失败 / 唯一键冲突 / 未知异常，
   未知异常只对外返回"系统繁忙"，堆栈只进日志，不泄露内部结构。

## 六、单元测试（论文第 5 章"系统测试"实证）

后端 `src/test/java/` 下有 36 个 JUnit 5 单元测试，覆盖：

| 测试类 | 覆盖点 |
| --- | --- |
| `OrderServiceImplTest` | 并发锁定防超卖、订单号/金额/商品快照、付款状态机、重复付款拦截、越权校验、超时自动取消、商品删除后快照兜底 |
| `GoodsServiceImplTest` | 后端裁决发布字段、价格校验、普通/管理员权限边界、锁定商品保护 |
| `UserServiceImplTest` | BCrypt 加密入库、明文密码渐进迁移、登录失败不枚举账号、禁用账号拦截 |
| `AiServiceImplTest` | 防幻觉事实核对：正常顿号分句不被误伤、编造商品名/错误报价被拦截 |
| `JwtInterceptorTest` | 禁用账号旧 token 即时失效、账号删除、token 解析失败、上下文清理 |

运行方式：`mvn test`（或在 IDEA 中右键 `src/test/java` → Run 'All Tests'）。
测试用 Mockito 隔离数据库，无需启动 MySQL；`LambdaCacheInit` 预热 MyBatis-Plus 列缓存，避免脱离 Spring 容器时 Lambda 条件构造器报错。

## 七、成绩与毕设材料

- 论文正文第 2~7 章大纲：相关技术 → 需求分析 → 系统设计 → 系统实现 → 系统测试 → 总结展望
- 图表建议：系统架构图、功能模块图、E-R 图、用例图、订单状态机图、测试用例表
- **系统测试章节可直接引用上述 36 个用例的覆盖矩阵和通过结果**

## 八、常见问题

| 现象 | 原因 / 处理 |
| --- | --- |
| 启动报 `Public Key Retrieval is not allowed` | JDBC URL 加 `allowPublicKeyRetrieval=true`（已配置） |
| 上传的图片前端 404 | `vite.config.js` 已把 `/uploads` 代理到 8080，改端口要同步改 |
| 打包成 jar 后刷新页面 404 | 已由 `SpaFallbackConfig` 处理：找不到静态文件时回退 `index.html` |
| 字段名不能用 `condition` | MySQL 保留字，成色字段叫 `item_condition` |
| AI 页面返回"已用本地关键词检索" | 未配置 Key 时自动降级，属正常现象。想启用大模型：设系统环境变量 `AI_API_KEY=你的智谱Key` 后重启后端即可；**不要把 Key 写进 yml**（历史 Key 视为已泄露，须先去智谱后台吊销轮换） |

> 安全提示：`application.yml` 中数据库密码、`jwt.secret` 仍为明文（课程作业可接受）。论文/答辩中应说明生产环境做法：密钥一律环境变量注入、数据库用最小权限账号、密钥定期轮换。

## 九、打成单个 jar（答辩现场用）

仍在项目根目录执行（相对路径，换电脑不用改）：

```powershell
cd campus-trade-frontend
npm.cmd run build                      # 产出 dist/

# 把 dist 内容复制进后端静态资源目录
Copy-Item -Recurse -Force dist\* ..\campus-trade-backend\src\main\resources\static\

cd ..\campus-trade-backend
mvn clean package -DskipTests
java -jar target\campus-trade-backend-1.0.0.jar
```

然后只需访问 http://localhost:8080 一个地址，前端路由由 `SpaFallbackConfig` 接管。
