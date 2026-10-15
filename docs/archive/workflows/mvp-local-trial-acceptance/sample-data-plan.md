# Sample Data Plan

## 目标

为 MVP 本地试运行准备 3–5 条少量、人工改写、仅本地使用的算法练习样例，用于验证完整链路：

```text
subject → knowledge point → question draft → question → mistake draft → mistake
→ review item → review record → attachment upload/link/read
```

## 使用边界

- 样例来源仅作为人工参考，不抓取、不批量、不接 API。
- 不复制 LeetCode 原题全文。
- 不公开发布到 `/blog`、`/notes`、`/mistakes`。
- 不加入公开题库或公开附件。
- 不把本计划扩展为导入脚本、题库迁移或批量数据功能。

## 统一来源标注

每条样例录入时建议使用以下来源标注：

```yaml
source_type: manual
source_title: LeetCode 相关练习
source_note: 仅用于本地试运行，不公开展示
```

## 统一命名前缀

建议本地试运行数据统一使用：

```text
LT-20260704
```

示例：

- Subject：`LT-20260704 Algorithms`
- Knowledge Point：`LT-20260704 Hash Table`
- Attachment：`LT-20260704-two-sum-note.txt`

## Subject 计划

| 字段 | 建议值 |
| --- | --- |
| name | LT-20260704 Algorithms |
| description | MVP 本地试运行专用科目，不公开展示 |
| visibility | 管理端本地试运行 |

## Knowledge Point 计划

| key | name | 用途 |
| --- | --- | --- |
| hash-table | LT-20260704 Hash Table | Two Sum |
| stack | LT-20260704 Stack | Valid Parentheses |
| tree-bfs | LT-20260704 Tree BFS | Binary Tree Level Order Traversal |
| dynamic-programming | LT-20260704 Dynamic Programming | Coin Change |
| sliding-window | LT-20260704 Sliding Window | Longest Substring Without Repeating Characters |

## 样例 1：Two Sum 相关练习

| 字段 | 计划 |
| --- | --- |
| sample_key | two-sum |
| 题型 | 简答 / 编程思路记录 |
| 知识点 | LT-20260704 Hash Table |
| 改写题意 | 给定一个整数列表和目标值，说明如何找到两个不同位置的数字，使它们的和等于目标值。 |
| 我的错误样例 | 忘记处理“不能重复使用同一位置”的约束。 |
| 正确思路摘要 | 用哈希表保存已见数字及位置，遍历时检查目标差值是否已出现。 |
| 附件建议 | 一张本地手写思路图或 `.txt` 复盘，不包含原题截图。 |

## 样例 2：Valid Parentheses 相关练习

| 字段 | 计划 |
| --- | --- |
| sample_key | valid-parentheses |
| 题型 | 判断题 / 简答 |
| 知识点 | LT-20260704 Stack |
| 改写题意 | 判断一个只包含括号字符的字符串是否满足每个右括号都能按正确顺序匹配最近的左括号。 |
| 我的错误样例 | 只统计数量相等，没有检查嵌套顺序。 |
| 正确思路摘要 | 使用栈保存左括号，遇到右括号时检查栈顶类型是否匹配。 |
| 附件建议 | 本地 `.txt` 记录几个自写反例，例如 `([)]`。 |

## 样例 3：Binary Tree Level Order Traversal 相关练习

| 字段 | 计划 |
| --- | --- |
| sample_key | tree-level-order |
| 题型 | 简答 / 数据结构流程 |
| 知识点 | LT-20260704 Tree BFS |
| 改写题意 | 给定一棵二叉树，按从上到下、从左到右的层级顺序输出每一层的节点值。 |
| 我的错误样例 | 队列遍历时没有固定当前层长度，导致层级边界混乱。 |
| 正确思路摘要 | 每轮先记录队列当前长度，只处理这一层的节点，再加入下一层子节点。 |
| 附件建议 | 本地画一棵小树的层序遍历示意图。 |

## 样例 4：Coin Change 相关练习

| 字段 | 计划 |
| --- | --- |
| sample_key | coin-change |
| 题型 | 简答 / 状态转移 |
| 知识点 | LT-20260704 Dynamic Programming |
| 改写题意 | 给定若干硬币面额和一个目标金额，求组成该金额所需的最少硬币数；无法组成时返回失败。 |
| 我的错误样例 | 贪心选择最大面额，忽略某些组合下并非最优。 |
| 正确思路摘要 | 使用动态规划，`dp[x]` 表示组成金额 x 的最少硬币数。 |
| 附件建议 | 本地 `.txt` 写出小金额的 dp 表。 |

## 样例 5：Longest Substring Without Repeating Characters 相关练习

| 字段 | 计划 |
| --- | --- |
| sample_key | longest-substring |
| 题型 | 简答 / 双指针流程 |
| 知识点 | LT-20260704 Sliding Window |
| 改写题意 | 给定一个字符串，求不含重复字符的最长连续片段长度。 |
| 我的错误样例 | 遇到重复字符时左边界只移动一格，导致窗口里仍有重复。 |
| 正确思路摘要 | 使用滑动窗口和字符最近位置，重复时把左边界移动到冲突位置之后。 |
| 附件建议 | 本地 `.txt` 记录窗口移动过程。 |

## 最小试运行组合

如果时间有限，先执行前三条：

1. Two Sum 相关练习。
2. Valid Parentheses 相关练习。
3. Binary Tree Level Order Traversal 相关练习。

如果前三条全部通过，再执行 Coin Change 与 Longest Substring，用于覆盖 DP 和 Sliding Window。
