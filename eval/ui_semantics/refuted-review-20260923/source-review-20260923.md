# 被否定候选复查：Umami、Paperless-ngx、Ghost 的 37 条（2026-09-23）

**历史记录。** 本文件保留初审及后续调查当时的分析和裁定建议。已完成的 D8、D9 裁定和当前最终分类见[评审总览](../../../docs/REFUTED-REVIEW.md)；下文历史分类和表格原样保留。

M12 判为 `refuted` 的候选不进入 M14 套件；被测应用本身有缺陷时，正确的候选恰恰会在这里被驳回。Conduit/RWA 的历史复查涵盖 57 条候选（8 关联真实缺陷 / 40 候选自身错误 / 8 不适定验证场景 / 1 待复现）；本文件按同一分类记录其余 37 条（Umami 2、Paperless-ngx 33、Ghost 2），五应用合计 94 条。

**方法与性质。** 复查采用 AI 辅助分析，依据为三类已有材料：冻结的 M12 执行证据（`M12/<candidate>/execution_evidence.json` 里逐检查点的请求与响应）、M10 候选定义（`M10/union/candidate_set.json` 的 `payload.primary_predicate`）、以及与部署镜像同版本的源码。分类阶段未重新运行候选生成流程或 `scripts/uisemtest*`；冻结结果、标签和审计文件保持原样。为读取固定版源码，以 `docker run --rm --entrypoint sh <image> -c 'cat …'` 的方式短暂进入镜像文件系统（不发布端口、不启动应用、退出即删）；**分类阶段（§1–§4）没有启动任何被测应用的部署栈**，原因见 §4。§5 是 2026-09-23 追加的受控复现，启动过 Paperless 固定版栈并已停栈，起停记录见 §5.1 与 §7。

历史复查采用以下分类码：**RD**＝关联真实缺陷（被否定的关系本应成立，固定版行为与功能说明/上游预期不符，且已受控复现）；**RD?**＝待复现（疑似缺陷但本轮未复现）；**WH**＝候选自身错误（关系提法错误，例如把非不变量当不变量、把分页总数当本页条数、角色绑定错资源）；**IP**＝不适定验证场景（前提未能重建、观察范围/数据量使场景无法判定）。四个码与 [Conduit/RWA 历史复查](../../../docs/REFUTED-REVIEW.md#historical-conduitrwa-review-2026-09-12)一致。

## 1. 取数口径与合计

运行根：Umami `full-01`、Paperless-ngx `m11fix-03` → `full-01`、Ghost `full-01`；每个用例取第一个含完整 M14 套件的运行。逐条初审标签、理由及证据位置见同目录的 [`refuted-review-20260923.json`](refuted-review-20260923.json)，对应可读清单见 [`refuted-review-20260923.md`](refuted-review-20260923.md)和[逐条表](逐条表-20260923.md)。

抽出的条数与文 27 §12「反驳」列一致：Umami 2、Paperless-ngx 33、Ghost 2，合计 37。**用例定位更正**：Paperless 的「多条」集中在 `L1-DOCLIST-07`（15 条），不是 `L1-DOCDETAIL-01`（2 条）。

| 应用 | 关联真实缺陷 RD | 待复现 RD? | 候选自身错误 WH | 不适定验证场景 IP | 未分类 | 合计 |
|---|---:|---:|---:|---:|---:|---:|
| Umami | 0 | 0 | 2 | 0 | 0 | 2 |
| Paperless-ngx | 0 | 0 | 19 | 14 | 0 | 33 |
| Ghost | 0 | 0 | 2 | 0 | 0 | 2 |
| **三应用合计** | **0** | **0** | **23** | **14** | **0** | **37** |

五应用合计（加上 Conduit/RWA 的 8/1/40/8）见文 27 §19。

## 2. 成因组（同成因合并说明，标签仍逐条给）

37 条归入 7 个成因组，**没有一条指向被测应用的真实缺陷**。

| 组 | 条数 | 应用 / 用例 | 一句话成因 | 分类 |
|---|---:|---|---|---|
| U1 | 1 | Umami `L2-USER-02` | 用户名按设计折小写，候选把提交值当作原样保存 | WH |
| U2 | 1 | Umami `L3-TEAM-04` | 成员取自 TeamUser 记录、集合是 Team 列表，`$.id` 对 `$.id` 永不匹配 | WH |
| P1 | 7 | Paperless `L1-DASHBOARD-03`、`L1-DOCDETAIL-01/02`、`L1-SETTINGS-03`、`L2-DOCEDIT-01/02`、`L3-SHARING-01` | `ui_settings.permissions` 去掉 app 前缀后不同 app 的同名 codename 相撞，元素唯一不是该字段的不变量 | WH |
| P2 | 11 | Paperless `L1-DOCDETAIL-01/02/05`、`L1-DOCLIST-03/05/07`、`L3-SHARING-01/02` | 把分页端点的 `$.count`（结果集总数）当作本页 `$.results` 的条数 | WH |
| P3 | 14 | Paperless `L1-DOCLIST-07` | owner 过滤在本场景无处理效应，且第 1 页只覆盖 61 条中的 50 条、排序键非全序，页窗口上无法判定子集关系 | IP |
| P4 | 1 | Paperless `L3-SHARING-02` | `date_joined` 是 ISO-8601 时间戳，候选定成 `yyyy-mm-dd` | WH |
| G1 | 2 | Ghost `L1-POST-05`、`L1-POST-08` | `published_at` 是 ISO-8601 时间戳，候选定成 `yyyy-mm-dd` | WH |

### U1 — Umami 用户名按设计折小写（1 条，WH）

候选 `v2-candidate-0027`（C02/V4，P02 eq）要求回读的 `$.username` 等于 `POST /api/users` 请求体里的 `username`。执行证据：请求体 `username="Test-user"`，**创建响应本身已经返回 `"test-user"`**，随后 `GET /api/users/4edb1936-…` 也是 `"test-user"`。

固定版 Umami 3.4.0（镜像 `ghcr.io/umami-software/umami@sha256:85909afc…`，`/app/package.json` 版本 3.4.0）的 `POST /api/users` 处理函数在创建时显式折小写：

```
// /app/.next/server/chunks/[root-of-the-server]__1zffp94._.js（turbopack 产物，偏移约 1851）
let{id:z,username:g,password:h,role:y}=u;
if(await (0,m.getUserByUsername)(g,{showDeleted:!0}))return (0,l.badRequest)({message:"User already exists"});
let v=await (0,m.createUser)({id:z||(0,o.uuid)(),username:g.toLowerCase(),password:(0,i.hashPassword)(h),role:y??n.ROLES.user});
```

查询侧 `getUserByUsername` 同样以 `where:{username:t.toLowerCase()}` 为键（同镜像 `[root-of-the-server]__0-5n6ml._.js` 偏移约 1044773），说明用户名是大小写不敏感的规范化标识，折小写是设计而非缺陷；`createUser` 自身不改写（`user.create({data:t,…})`），折小写发生在路由层。应用前后自洽（创建响应与回读一致），没有 Conduit `tagList` 那种「响应回显了未保存的值」的自相矛盾。**候选自身错误。**

### U2 — Umami 团队成员记录与团队列表的身份绑定错位（1 条，WH）

候选 `v2-candidate-0011`（C01/V4，P14 `added`）把 member 取自 producer 响应的 `$`——`POST /api/teams/join` 返回的是一条 **TeamUser 成员记录**（`id=a882e49e-…`，`role=team-member`，`teamId=8c9be843-…`）——再到 `GET /api/users/<id>/teams` 的 `$.data`（元素是 **Team**，`id=8c9be843-…`）里按 `$.id` 对 `$.id` 找，两类 id 属于不同实体，`before_matches` 与 `after_matches` 都是 0。加入团队实际成功：before `count=0`，after `count=1` 且该团队的 `members` 里含该用户。与先例 RWA `POST /likes` 响应是纯文本 `OK` 却按 `$.id` 匹配的两条同类（角色绑定错资源）。**候选自身错误。**

### P1 — Paperless `ui_settings.permissions` 去掉 app 前缀后必然重复（7 条，WH）

候选（P15 唯一性）要求 `GET /api/ui_settings/` 的 `$.permissions` 数组元素互不相同。实测 166 个元素里 162 个不同，重复的恰好是 `change_logentry`（index 4 与 20）、`delete_logentry`（61 与 127）、`add_logentry`（85 与 143）、`view_logentry`（118 与 141）各两次。

固定版 3.2.0 源码（镜像 `ghcr.io/paperless-ngx/paperless-ngx@sha256:22dc423f…`，`src/paperless/version.py` 为 `(3, 2, 0)`）：

```python
# src/documents/views.py:4287-4288
        # strip <app_label>.
        roles = map(lambda perm: re.sub(r"^\w+.", "", perm), user.get_all_permissions())
```

`user.get_all_permissions()` 返回 `"<app_label>.<codename>"` 的集合；去掉 app 前缀后，不同 app 的同名 codename 就会相撞。本实例同时装了两个定义 `LogEntry` 的 app：`django.contrib.admin`（`src/paperless/settings/__init__.py:148`）与 `auditlog`（同文件 `:1046` 在审计日志开启时追加），实测响应里 `settings.auditlog_enabled=true`。因此「元素唯一」不是该字段的不变量，是把非不变量当不变量。**候选自身错误**（与先例 RWA「每条通知都有 string 型 status」同类）。

### P2 — 把分页端点的 `$.count` 当作本页条数（11 条，WH）

候选（P19 `count`）要求 `GET /api/documents/` 响应的 `$.count` 等于本页 `$.results` 的元素个数。`$.count` 是整个结果集的总数：

```python
# src/paperless/views.py:61-83  class StandardPagination(PageNumberPagination)
    def get_paginated_response(self, data):
        response_data = [
            ("count", self.page.paginator.count),
            …
```

11 条里 8 条的观测是 `page_size=1` / `$.count=8`（查询 `tags__id__all=1`），3 条是 `page_size=50` / `$.count=61`，都是跨页情形。该端点在文 27 §15 的 `PAGINATED` 名单内（`("paperless", "/api/documents/")`），与 Conduit/RWA 先例里 8 条 `results count == pageData.limit`（`refuted-review-final-20260912.md` 第 20、22、29、49、50、51、52、55 行）同源。M12 驳回正确。**候选自身错误。**

### P3 — `L1-DOCLIST-07` 的 owner 过滤子集关系在第 1 页窗口上不可判定（14 条，IP）

候选（C08/V3，P17 `subset`）要求 `followup_query:q1`（`GET /api/documents/?owner__id__in=2&ordering=-created&page=1&page_size=50&include_selection_data=true&truncate_content=true`）的 `$.results` 按 `$.id` 是 `source_query`（同端点、同参数但不带 `owner__id__in`）`$.results` 的子集。三项实测：

1. **过滤没有处理效应**：两次查询的 `$.count` 都是 **61**，返回文档的 `owner` 全部为 `2`，即 `owner__id__in=2` 选中了全部文档。
2. **页窗口只覆盖 61 条中的 50 条**：两侧各返回 50 条，交集 42；过滤侧独有 `{5, 55, 56, 57, 58, 59, 60, 61}`，不过滤侧独有 `{12, 13, 14, 15, 16, 17, 18, 19}`。
3. **排序键不是全序**：`Document.created` 是 `models.DateField`（`src/documents/models.py:247-251`，日粒度），这 61 份文档只有 3 个不同日期（`2021-01-01`、`2022-12-11`、`2026-09-20`）；`Meta.ordering = ("-created",)`（`models.py:340-341`）与 `DocumentsOrderingFilter`／`ordering_fields`（`src/documents/views.py:1031-1045`）都没有次级键，并列行的返回顺序随执行计划而变，而两侧的 SQL 因多了 owner 过滤本来就不同。

所以被否定的**不是**「过滤结果 ⊆ 未过滤结果」这条业务关系（它在完整结果集上成立：两边都是同一批 61 份），而是把该关系落在第 1 页窗口上的**这个实例**：数据量（61 > 50）加上非全序排序使场景无法判定，既不是缺陷也不是候选命题本身错误。按 4.6 口径归入**不适定验证场景**。

补充两点事实：(a) 这 14 条候选除 `candidate_id` 与所引 `evidence_card_id`（两个卡之一）外**完全相同**——同一 producer/consumer 请求引用 `r20260920-085841-faf8:request:9` / `:66`，同一谓词、同一 identity、同一 projection，是同一命题的 14 份重复；(b) 「同一排序下两次查询的第 1 页成员不同」这一现象本身是否会让用户在翻页时重复看到/漏看文档，本轮**未核实**（需要独立复现才能判断，见 §4），本文件不把它计为缺陷，也不计为待复现。**2026-09-23 补：§5 已受控复现，会重复看到也会漏看，判定为应用缺陷；这 14 条是否改判 RD 见 §5.6（本节 IP 标签暂不改动，等作者裁定）。**

### P4 / G1 — 日期格式被定成 `yyyy-mm-dd`（3 条，WH）

- Paperless `L3-SHARING-02 / v2-candidate-0075`：`forall` + P10 `date_yyyy_mm_dd` 作用在 `GET /api/users/` 每个结果的 `$.date_joined`；实测是 `2026-09-20T12:06:20.641751Z`（2 条结果全不符）。`date_joined` 是 Django `auth.User` 的 `DateTimeField`，DRF 按 ISO-8601 序列化。
- Ghost `L1-POST-05 / v2-candidate-0047`、`L1-POST-08 / v2-candidate-0030`：同一形状的谓词作用在 `GET /ghost/api/admin/posts/` 每个 `$.published_at`；实测是 `2026-09-20T15:53:05.000Z`。固定版 v5.130.6（本机 checkout `~/APITest/UISemTest-subjects/ghost`，HEAD `a07c753c8a` = `v5.130.6`，与 `deploy/ghost/README.md` 记录的上游 tag 一致）的输出序列化器一律转 ISO-8601：

```js
// ghost/core/core/server/api/endpoints/utils/serializers/output/utils/date.js:4-18
const format = (date) => moment(date).tz(settingsCache.get('timezone')).toISOString(true);
const forPost = (attrs) => { ['created_at', 'updated_at', 'published_at'].forEach(…); };
```

与 Conduit/RWA 先例中 12 条把日期时间字段（`createdAt`/`modifiedAt`/`requestResolvedAt`）误定为 `yyyy-mm-dd` 的候选完全同源（同文件第 5、6、25、31–36、42、43、54 行）。M12 驳回正确。**候选自身错误。**

## 3. 逐条表

| # | 应用 | 用例 / 候选 | 契约/计划 | producer | observer | 主谓词 | 失败观测（执行证据实测值） | 分类 | 成因组 |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | Umami | L2-USER-02 / v2-candidate-0027 | C02/V4 | actor_a POST /api/users | actor_a GET /api/users/069d698b-b541-40ca-8bee-d5b9a1752f0a | P02 eq after $.username | after $.username="test-user"，producer_request $.username="Test-user" | 候选自身错误（WH） | U1 |
| 2 | Umami | L3-TEAM-04 / v2-candidate-0011 | C01/V4 | actor_b POST /api/teams/join | actor_b GET /api/users/b0000000-0000-4000-8000-000000000002/teams | P14 added id=[{"collection_item_path": "$.id", "member_path": "$.id"}] | before_matches=0、after_matches=0；member 取 producer_response $.id=a882e49e-abed-46ff-9912-1e7a53a2e7d5（TeamUser 成员记录），集合 $.data 元素的 $.id=8c9be843-a920-4e18-b6be-a46af534b802（Team）；before count=0 → after count=1 | 候选自身错误（WH） | U2 |
| 3 | Paperless-ngx | L1-DASHBOARD-03 / v2-candidate-0029 | single_state_constraint/V2 | - | actor_a GET /api/ui_settings/ | P15 over $.permissions id=["$"] | member_count=166，重复 4 项（index 20, 127, 141, 143 分别与 index 4, 61, 118, 85 同值，均为 *_logentry） | 候选自身错误（WH） | P1 |
| 4 | Paperless-ngx | L1-DOCDETAIL-01 / v2-candidate-0015 | single_state_constraint/V2 | - | actor_a GET /api/ui_settings/ | P15 over $.permissions id=["$"] | member_count=166，重复 4 项（index 20, 127, 141, 143 分别与 index 4, 61, 118, 85 同值，均为 *_logentry） | 候选自身错误（WH） | P1 |
| 5 | Paperless-ngx | L1-DOCDETAIL-01 / v2-candidate-0030 | single_state_constraint/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=8，len($.results)=1（page_size=1） | 候选自身错误（WH） | P2 |
| 6 | Paperless-ngx | L1-DOCDETAIL-02 / v2-candidate-0017 | single_state_constraint/V2 | - | actor_a GET /api/ui_settings/ | P15 over $.permissions id=["$"] | member_count=166，重复 4 项（index 20, 127, 141, 143 分别与 index 4, 61, 118, 85 同值，均为 *_logentry） | 候选自身错误（WH） | P1 |
| 7 | Paperless-ngx | L1-DOCDETAIL-02 / v2-candidate-0032 | single_state_constraint/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=8，len($.results)=1（page_size=1） | 候选自身错误（WH） | P2 |
| 8 | Paperless-ngx | L1-DOCDETAIL-05 / v2-candidate-0021 | single_state_constraint/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=8，len($.results)=1（page_size=1） | 候选自身错误（WH） | P2 |
| 9 | Paperless-ngx | L1-DOCDETAIL-05 / v2-candidate-0089 | C14/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=8，len($.results)=1（page_size=1） | 候选自身错误（WH） | P2 |
| 10 | Paperless-ngx | L1-DOCLIST-03 / v2-candidate-0035 | single_state_constraint/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=61，len($.results)=50（page_size=50） | 候选自身错误（WH） | P2 |
| 11 | Paperless-ngx | L1-DOCLIST-03 / v2-candidate-0036 | single_state_constraint/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=8，len($.results)=1（page_size=1） | 候选自身错误（WH） | P2 |
| 12 | Paperless-ngx | L1-DOCLIST-05 / v2-candidate-0003 | C14/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=61，len($.results)=50（page_size=50） | 候选自身错误（WH） | P2 |
| 13 | Paperless-ngx | L1-DOCLIST-05 / v2-candidate-0028 | C14/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=8，len($.results)=1（page_size=1） | 候选自身错误（WH） | P2 |
| 14 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0009 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 15 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0014 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 16 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0015 | single_state_constraint/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=61，len($.results)=50（page_size=50） | 候选自身错误（WH） | P2 |
| 17 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0016 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 18 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0017 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 19 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0026 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 20 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0035 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 21 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0037 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 22 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0038 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 23 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0039 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 24 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0040 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 25 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0042 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 26 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0043 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 27 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0044 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 28 | Paperless-ngx | L1-DOCLIST-07 / v2-candidate-0045 | C08/V3 | actor_a GET /api/documents/ | actor_a GET /api/documents/ | P17 subset followup_query:q1 $.results ⊆ source_query $.results id=["$.id"] | left（q1，owner__id__in=2）count=61、本页 50 条；right（source，无 owner 过滤）count=61、本页 50 条；relation=false（交集 42，两侧各 8 条独有） | 不适定验证场景（IP） | P3 |
| 29 | Paperless-ngx | L1-SETTINGS-03 / v2-candidate-0008 | single_state_constraint/V2 | - | actor_a GET /api/ui_settings/ | P15 over $.permissions id=["$"] | member_count=166，重复 4 项（index 20, 127, 141, 143 分别与 index 4, 61, 118, 85 同值，均为 *_logentry） | 候选自身错误（WH） | P1 |
| 30 | Paperless-ngx | L2-DOCEDIT-01 / v2-candidate-0029 | single_state_constraint/V2 | - | actor_a GET /api/ui_settings/ | P15 over $.permissions id=["$"] | member_count=166，重复 4 项（index 20, 127, 141, 143 分别与 index 4, 61, 118, 85 同值，均为 *_logentry） | 候选自身错误（WH） | P1 |
| 31 | Paperless-ngx | L2-DOCEDIT-02 / v2-candidate-0003 | single_state_constraint/V2 | - | actor_a GET /api/ui_settings/ | P15 over $.permissions id=["$"] | member_count=166，重复 4 项（index 20, 127, 141, 143 分别与 index 4, 61, 118, 85 同值，均为 *_logentry） | 候选自身错误（WH） | P1 |
| 32 | Paperless-ngx | L3-SHARING-01 / v2-candidate-0019 | single_state_constraint/V2 | - | actor_a GET /api/ui_settings/ | P15 over $.permissions id=["$"] | member_count=166，重复 4 项（index 20, 127, 141, 143 分别与 index 4, 61, 118, 85 同值，均为 *_logentry） | 候选自身错误（WH） | P1 |
| 33 | Paperless-ngx | L3-SHARING-01 / v2-candidate-0059 | C14/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=8，len($.results)=1（page_size=1） | 候选自身错误（WH） | P2 |
| 34 | Paperless-ngx | L3-SHARING-02 / v2-candidate-0018 | C14/V2 | - | actor_a GET /api/documents/ | P19 count over $.results == $.count | $.count=8，len($.results)=1（page_size=1） | 候选自身错误（WH） | P2 |
| 35 | Paperless-ngx | L3-SHARING-02 / v2-candidate-0075 | single_state_constraint/V2 | - | actor_a GET /api/users/ | forall over $.results / P10 date_yyyy_mm_dd $.date_joined | applicable_member_count=2，format_valid=false 的成员 2 个 | 候选自身错误（WH） | P4 |
| 36 | Ghost | L1-POST-05 / v2-candidate-0047 | single_state_constraint/V2 | - | actor_a GET /ghost/api/admin/posts/ | forall over $.posts / P10 date_yyyy_mm_dd $.published_at | applicable_member_count=1，format_valid=false 的成员 1 个 | 候选自身错误（WH） | G1 |
| 37 | Ghost | L1-POST-08 / v2-candidate-0030 | single_state_constraint/V2 | - | actor_a GET /ghost/api/admin/posts/ | forall over $.posts / P10 date_yyyy_mm_dd $.published_at | applicable_member_count=1，format_valid=false 的成员 1 个 | 候选自身错误（WH） | G1 |

逐条表与上表由同一份标签渲染，完整版（含每条的证据文件路径）在 `eval/ui_semantics/refuted-review-20260923/逐条表-20260923.md` 与 `refuted-review-20260923.md`。

## 4. 受控复现：本轮没有触发

可以对「疑似真实缺陷」的候选启动固定版容器做受控复现。**37 条里没有一条被判为疑似真实缺陷（RD 0、RD? 0），因此本轮没有启动任何被测应用的部署栈**，`eval/ui_semantics/bug-leads-20260923/` 没有创建。

逐条排除理由（对最像缺陷的三项）：

| 观测 | 为什么不构成缺陷线索 |
|---|---|
| Umami 把提交的 `Test-user` 存成 `test-user` | 创建响应本身就返回规范化后的值，查询侧同样折小写；应用自洽，属设计（§2 U1）。不同于 Conduit 的 `tagList`：那里创建响应原样回显了**未被保存**的标签，响应与状态互相矛盾，才是缺陷 |
| Paperless `ui_settings.permissions` 里有 4 组重复 | 重复来自「去掉 app 前缀」这一步（源码带注释的既定行为），重复元素是同一字符串，不改变 UI 端 `includes(codename)` 判定的结果；是接口表示上的歧义，不是功能错误（§2 P1） |
| Paperless 同一排序下两次查询的第 1 页成员不同 | 直接成因是排序键并列（`created` 为日粒度 `DateField`，61 份文档仅 3 个不同日期）且两次查询 SQL 不同；「用户翻页时是否会重复看到/漏看文档」需要在干净环境里连续取 page 1 / page 2 才能判断，本轮**未核实**，不计入缺陷也不计入待复现（§2 P3） |

P3 分页线索的后续独立复现见 §5；固定版本、种子数据、请求参数与已执行的对照均以该节及存档脚本、响应记录为准。

**与上游仓库的关系**：由于没有 RD/RD? 项，本轮不需要对照上游 issue/PR；对三个应用的上游仓库**未做**检索。

> **2026-09-23 补记**：对上表的分页线索开展独立复现，确认显式排序下的跨页重复与遗漏，结论见 **§5**。本节保留初审阶段的原始状态。

## 5. 受控复现：Paperless 显式 `ordering=-created` 翻页重复与漏看（2026-09-23）

§4 所列分页线索经本节独立实验确认存在跨页重复与遗漏，判定为**应用缺陷**。产物目录 `eval/ui_semantics/bug-leads-20260923/paperless-pagination/`：脚本 `reproduce_paperless_pagination.py`、`evidence.jsonl`（157 条 HTTP 记录，全部 200）、`summary.json`。独立复现脚本通过 Python 标准库直接发送 HTTP 请求，未调用模型或 Testimony 流水线；冻结结果、标签和审计文件保持原样。

### 5.1 环境、起停与数据

- 部署用 RQ2 同一套脚本：`deploy/paperless/stack.sh sidecars-up`（含 prewarm + 黄金种子）+ `python -m subject_adapters.docker_single_local supervise`。镜像 `ghcr.io/paperless-ngx/paperless-ngx@sha256:22dc423ff48ac1629977dbf0c9625ba9f60d3bd1291a2ff173c65351984a14c2`，`/usr/src/paperless/src/paperless/version.py` 为 `(3, 2, 0)`，**未打任何故障补丁**。启动前 `lsof -nP -iTCP:18091 -sTCP:LISTEN` 为空。
- 启动的容器只有三个：`uisemtest-paperless-ec06ccd83a891e2e`（应用）、`…-pg`、`…-valkey`。做完先对**本轮自己的** supervise 进程发 SIGTERM，再 `stack.sh down`；复核结果：`docker ps -a` 无 paperless 容器、`docker volume ls` 无 paperless 卷、端口 18091 已释放。
- 数据用干净黄金种子，未额外上传文档（并列已经足够，不需要放大）：61 份文档，`created` 只有 3 个值——`2021-01-01` 58 份、`2022-12-11` 2 份、`2026-09-23` 1 份（最后一个是 `deploy/paperless/README.md` §3 说的 `timezone.localdate()`，随起栈当天变动）。

### 5.2 观测（全部出自 `evidence.jsonl`；157 条请求状态码全为 200）

| 阶段 | 请求 | 结果 |
|---|---|---|
| A 普查 | `?ordering=-created&page=1&page_size=100000` | `count=61`，本页 61 条，`created` 3 个不同值 |
| B 同一请求重复 12 次 | `?ordering=-created&page=1&page_size=50&include_selection_data=true&truncate_content=true` | 12 次的 id **顺序与成员完全一致**（`distinct_orders=1`、`distinct_member_sets=1`）：重复同一请求本身是稳定的 |
| **C 用户翻页（显式 `ordering=-created`）** | `page=1..N`，`page_size=50 / 20 / 10`，各 3 轮 | `page_size=50`：两页共 61 行却只有 **53 个不同 id**，`5,55,56,57,58,59,60,61` 各看两遍，`12–19` 一次都不出现；`page_size=20` 与 `10`：61 行里只有 **43 个不同 id**，18 个重复、18 个（`12–29`）从不出现。3 轮逐格相同 |
| E 对照：全序键 | `ordering=id`，`page_size=10`，3 轮 | 61 行 / 61 个不同 id，无重复无遗漏 |
| F 对照：多键（接口接受，200） | `ordering=-created,-id`，`page_size=10`，3 轮 | 61 行 / 61 个不同 id，无重复无遗漏 |
| **H 对照：不带 `ordering` 参数** | `page_size=50 / 10`，各 3 轮 | 61 行 / 61 个不同 id，无重复无遗漏 |
| I 显式升序键 | `ordering=created`，`page_size=10`，3 轮 | 61 行 / **57** 个不同 id，`9,42,43,44` 重复，`5,50,60,61` 不出现 |
| G M12 原对（带/不带 `owner__id__in=2`），5 轮 | `page=1&page_size=50` | 本轮两侧第 1 页**完全相同**，子集关系 5 轮都成立——M12 当时的跨查询差异本轮**未复现**（见 §5.6 保留意见 (a)） |

最直接的一对（`evidence.jsonl` 阶段 `C_sweep_ps50` 第 1 轮）：

```
GET /api/documents/?ordering=-created&page=1&page_size=50&include_selection_data=true&truncate_content=true
  200  count=61  page_len=50
  ids=[1,2,3,5,61,60,59,58,57,56,55,54,53,52,51,50,49,48,47,46,45,44,43,42,41,40,
       39,38,37,36,35,8,7,6,4,34,33,32,31,30,29,28,27,26,25,24,23,22,21,20]
GET /api/documents/?ordering=-created&page=2&page_size=50&include_selection_data=true&truncate_content=true
  200  count=61  page_len=11
  ids=[55,56,9,58,59,60,61,5,57,10,11]
```

两页合计 61 行，接口自报 `count=61`，但用户实际看到 53 份文档：8 份看了两遍，另外 8 份（id 12–19）在任何一页上都不出现。

（附带事实：响应里没有 `all` 字段——`StandardPagination._should_include_all` 只在 API 版本 < 10 时加，本实例默认版本 ≥ 10——所以阶段 J 的「`all` 列表是否完整」不适用。）

### 5.3 成因：固定版**已带**上游补丁，但补丁只覆盖默认排序

1. 固定版 3.2.0 的 `DocumentViewSet.get_queryset` 已经是带次级键的写法：

```python
# 镜像内 /usr/src/paperless/src/documents/views.py:1208-1211（同一 queryset 块延续到 1213）
        queryset = (
            Document.objects.filter(root_document__isnull=True)
            .order_by("-created", "-id")
            .annotate(num_notes=Coalesce(note_count, 0))
            …
```

也就是说 §4 与 §2 P3 里写的「`Meta.ordering = ("-created",)` 没有次级键」虽然对（`documents/models.py:341` 确实仍是 `ordering = ("-created",)`、`created` 仍是 `models.DateField`，`models.py:247-251`），但**列表端点实际用的不是 `Meta.ordering`**，而是 `get_queryset` 里这一行。

2. 真正的缺口在显式 `ordering=` 这条路径。DRF 的排序后端是**替换**而不是追加：

```python
# 镜像内 /usr/local/lib/python3.14/site-packages/rest_framework/filters.py:320-326
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            return queryset.order_by(*ordering)
        return queryset
```

`documents/filters.py:1097-1235` 的 `DocumentsOrderingFilter` 只额外处理 `custom_field_` 前缀，最后一行仍是 `return super().filter_queryset(request, queryset, view)`，不补次级键。所以客户端一旦送 `ordering=-created`，`-id` 就被丢掉，排序退回到日粒度单键；不送 `ordering` 时才受 `get_queryset` 的 `-id` 保护。阶段 C/I（送了）与阶段 H（没送）的对照正好把这条路径差别量了出来。

3. 数据库侧（`docker exec <pg> psql`，PostgreSQL 17.11）：`ORDER BY created DESC LIMIT 50 OFFSET 0` 与 `… OFFSET 50` 的计划都是 `Limit -> Sort -> Seq Scan`、`Sort Method: quicksort`，但两次 `Sort` 节点吐出的行数不同（`actual rows=50` 对 `actual rows=61`，下层 `Seq Scan` 两次都是 61）。**就这条最简 SQL 而言两页恰好互补**（`1,2,3,12..34,4,6,7,8,35..54` 与 `55,56,9,58,59,60,61,5,57,10,11`，并集 61、无重复）——即并列行的落位取决于计划，数据库**不作保证**；API 的 queryset 还多了 `filter(root_document__isnull=True)`、`annotate`、`select_related/prefetch_related` 与权限过滤，计划不同，重复与漏看就出现了。这一条是机制说明，不是缺陷证据；缺陷证据是 §5.2 的 API 观测。

### 5.4 上游核对（2026-09-23 取）

| 项 | 事实 |
|---|---|
| issue [#12437](https://github.com/paperless-ngx/paperless-ngx/issues/12437) | 「Paged output of documents may contain duplicates shadowing other results」，作者 bronger，2026-03-26 开，针对 2.20.10，已关闭。报告的现象与本节一致：翻页时同一 id 多次出现（尤其在页边界），因而遮住别的文档，而 `count` 是对的 |
| PR [#12440](https://github.com/paperless-ngx/paperless-ngx/pull/12440) | 「Fix: add fallback ordering for documents by id after created」，shamoon，2026-03-26 合入 `release/v2.20.x`，里程碑 v2.20.14，closes #12437。diff（`…/pull/12440.diff`）只有两处：`src/documents/views.py` 的 `.order_by("-created")` → `.order_by("-created", "-id")`，加一条**只测默认排序**（请求不带 `ordering`）的用例 `test_default_ordering_uses_id_as_tiebreaker` |
| 固定版是否含该补丁 | **含**。v3.2.0 发布于 2026-09-19（`961f018d3e6d` = "Bump version to 3.2.0"，也是镜像的 OCI revision；官方 UI 测试及 seed 来源为 `54e332d259436b0b5cb5e8f38753a83797924135`，2026-09-20），`views.py:1210` 已是 `.order_by("-created", "-id")` |
| 上游 main 现状 | 今天取 raw 文件：`src/documents/views.py` 第 1210 行仍是 `.order_by("-created", "-id")`（与固定版逐行一致），`src/documents/filters.py:1097-1235` 的 `DocumentsOrderingFilter` 仍以 `return super().filter_queryset(...)` 结尾。**显式 `ordering=` 路径在 main 上仍未修** |
| 有无针对显式排序的上游报告 | 截至 2026-09-23，两次 GitHub 站内检索（pagination duplicate / unstable ordering / ordering created id）未检索到专门针对「显式 `ordering=` 仍无次级键」的 issue 或 PR。 |

**版本来源。** 固定部署版本为 v3.2.0，镜像由上述 digest 标识，OCI revision 为 `961f018d3e6d`；官方 UI 测试及 seed 实现的来源提交为 `54e332d259436b0b5cb5e8f38753a83797924135`。两项分别标识部署镜像和测试材料来源。

### 5.5 判定

按存档脚本、请求记录与摘要，复现结果及其范围如下：

1. **现象可稳定复现** — 显式降序 `ordering=-created` 在 `page_size=10/20/50` 下各重复三轮，显式升序 `ordering=created` 仅在 `page_size=10` 下重复三轮；各已执行组合内结果一致。`ordering=id` 与 `ordering=-created,-id` 的连续分页对照均为 `page_size=10`、各三轮，不带 `ordering` 的默认排序对照为 `page_size=10/50`、各三轮；这些已执行对照均无重复或遗漏。
2. **违反的业务规则说得清** — 同一排序下逐页翻完一个列表，每份文档应恰好出现一次，各页并集应覆盖接口自报的 `count`。实测 `count=61`，用户看到 53（`page_size=50`）或 43（10/20）份。
3. **上游状态明确** — 根因已被上游确认并修（#12437 / #12440，v2.20.14），但修复只覆盖默认排序；显式 `ordering=` 路径在固定版 3.2.0 与上游 main 上都仍有问题。

**结论：是应用缺陷**；独立复现确认的是显式排序下的跨页重复与遗漏。`L1-DOCLIST-07` 的原始 UI HAR（`eval/ui_semantics/paperless-20260921/recordings-01/cases/L1-DOCLIST-07/actors/actor_a/r20260920-085841-faf8/session_bundle/har.json`）已使用 `ordering=-created`，但其中三次文档列表请求均为 `page=1`，`page_size` 依次为 50、1、50。响应中的 `next` 可含 `page=2` URL，不能据其在 Flat 派生产物中出现而认定 UI 或 M12 已发送第 2 页请求。本节连续分页的实际请求记录来自独立复现脚本及 `evidence.jsonl`。

### 5.6 14 条候选的历史分析与既有裁定

2026-09-23 的[既有裁定](final-adjudication-source-20260923.json)已将 `L1-DOCLIST-07` 的 14 条候选关联至 D8；原始裁定和分类记录保持原样。[简洁阅读版](../../../docs/D8-ADJUDICATION-SOURCE-EXCERPT.md)列出来源哈希、原始行号及材料入口。以下分别说明原 M12 观测与独立复现所支持的范围。

- **原始比较条件。** 两侧 `count` 都是 61，全部文档 owner 都是 2；候选实际检查的是带／不带 `owner__id__in=2` 的第 1 页窗口，不能仅由完整文档集合的关系推出分页窗口检查必然通过。
- **原 M12 观测。** 代表性候选 `v2-candidate-0009` 的两侧第 1 页各有 50 个 ID，交集 42、两侧各 8 条独有。这是两个查询的同页比较，不是连续分页实验。
- **排序对照的范围。** 阶段 E/F 在 `page_size=10` 的连续分页中无重复或遗漏，支持对排序路径的分析；这些对照没有验证原 14 条同页候选在全序键下必然通过。
- 先例一致：表 V 的 D1 对应 5 条被否定候选，D2/D5/D7 各 1 条。

**证据范围与记录口径**：

(a) 阶段 G 的 5 轮中，两侧第 1 页完全相同、子集关系成立，原 M12 的同页窗口差异**未复现**。独立复现确认的是显式排序下连续翻页的重复与遗漏，不单独确证原同页差异的直接成因。14 条候选的 D8 关联依据既有裁定保留，不将该关联解释为原失败观测的逐字复现。

(b) 这 14 条是同一命题的 14 份重复（§2 P3 补充事实 (a)）。既有 D8 裁定使该历史阶段的关联候选数由 8 变成 22，其中 14 条关联同一个 D8；22 表示候选关联数，不表示 22 个独立缺陷或独立复现。

采用 D8 裁定后的分应用与五应用历史汇总如下（原记录对应文 27 §19.4；表中保留当时口径）：

| 应用 | 被否定候选 | 关联真实缺陷 RD | 待复现 RD? | 候选自身错误 WH | 不适定验证场景 IP |
|---|---:|---:|---:|---:|---:|
| Paperless-ngx | 33 | **14** | 0 | 19 | **0** |
| 三应用合计 | 37 | **14** | 0 | 23 | **0** |
| 五应用合计 | 94 | **22** | 1 | 63 | **8** |

## 6. 初审阶段与 Conduit/RWA 的对比

| 批次 | 被否定候选 | 关联真实缺陷 | 待复现 | 候选自身错误 | 不适定场景 |
|---|---:|---:|---:|---:|---:|
| Conduit + RWA（演示型应用，`refuted-review-final-20260912.md`） | 57 | 8 | 1 | 40 | 8 |
| Umami + Paperless-ngx + Ghost（成熟生产应用，本文件） | 37 | 0 | 0 | 23 | 14 |
| 五应用合计 | 94 | 8 | 1 | 63 | 22 |

该初审阶段的 8 条缺陷关联与 1 条待复现线索均来自 Conduit 与 RWA；另外三个应用的 37 条候选初审分类为候选错误或不适定场景。后续 D8 裁定及当前分类见下文链接。

**2026-09-23 裁定记录**：上表是 §1–§4 初审阶段的口径，未含 §5 的独立复现结论。既有 D8 裁定已将 `L1-DOCLIST-07` 的 14 条 IP → RD；对应阶段汇总为「37 | 14 | 0 | 23 | 0」与「94 | 22 | 1 | 63 | 8」。初审表格原样保留，当前最终分类见[评审总览](../../../docs/REFUTED-REVIEW.md)。

## 7. 材料入口

| 材料 | 路径 | 内容 |
|---|---|---|
| 逐条初审记录 | [`refuted-review-20260923.json`](refuted-review-20260923.json) | 37 条候选的初始分类、理由和证据位置 |
| 可读初审清单 | [`refuted-review-20260923.md`](refuted-review-20260923.md)、[逐条表](逐条表-20260923.md) | 对应逐条记录 |
| D8 复现脚本 | [`reproduce_paperless_pagination.py`](../bug-leads-20260923/paperless-pagination/reproduce_paperless_pagination.py) | 使用 Python 标准库直接发送 HTTP 请求 |
| D8 原始响应 | [`evidence.jsonl`](../bug-leads-20260923/paperless-pagination/evidence.jsonl) | 157 条 HTTP 记录 |
| D8 复现摘要 | [`summary.json`](../bug-leads-20260923/paperless-pagination/summary.json) | 已执行组合、对照及结果 |
| D8 简洁阅读版 | [历史裁定与证据](../../../docs/D8-ADJUDICATION-SOURCE-EXCERPT.md) | 来源哈希、原始行号和复现范围 |
| D8 历史裁定 | [`final-adjudication-source-20260923.json`](final-adjudication-source-20260923.json) | 原始裁定摘录及完整历史来源的哈希、行号 |
| 当前分类 | [`final-classifications-94.json`](final-classifications-94.json)、[评审总览](../../../docs/REFUTED-REVIEW.md) | 后续裁定后的最终分类与历史记录入口 |
