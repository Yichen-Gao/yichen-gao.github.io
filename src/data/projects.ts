export type Project = {
  title: string;
  period: string;
  category: string;
  summary: string;
  outcome: string;
  stack: string[];
  href?: string;
  featured?: boolean;
};

export const projects: Project[] = [
  {
    title: 'Labflow',
    period: '工具链 / 持续迭代中',
    category: '科研工作流自动化',
    summary:
      '面向研究与实验管理的工作流工具，目标是把任务拆解、结果沉淀、协作交接和复盘过程整理得更顺畅。',
    outcome:
      '适合作为求职时的案例：它不是单点脚本，而是把真实效率痛点抽象成可复用系统的工程思路。',
    stack: ['Python', 'Automation', 'Experiment Ops'],
    href: 'https://github.com/Yichen-Gao/Labflow',
    featured: true,
  },
  {
    title: '多模态评测工作台',
    period: '研究项目',
    category: '评测与分析',
    summary:
      '围绕音频或多模态语言任务整理 benchmark、误差分析和评测脚本，让模型能力与失败模式更容易被看清。',
    outcome:
      '这个方向能体现我不仅会跑模型，也会搭评测闭环，知道怎样把结果转化成可信结论。',
    stack: ['Python', 'Evaluation', 'Data Analysis'],
    featured: true,
  },
  {
    title: '研究自动化迭代链路',
    period: '内部工具化',
    category: '开发体验',
    summary:
      '把想法整理、实现、实验跟踪和审稿式回看串成一个更短的循环，减少重复劳动，提高试错效率。',
    outcome:
      '它展示的是系统视角：我关心的不只是模型本身，也关心团队如何更快地产出和复用结果。',
    stack: ['CLI', 'Prompt Workflows', 'Experiment Tracking'],
    featured: true,
  },
  {
    title: '待补充的代表项目',
    period: '建议尽快替换',
    category: '简历强化位',
    summary:
      '这里建议补上你最强的一段经历，比如实习、课程设计、论文项目、开源贡献或真正落地过的产品功能。',
    outcome:
      '最打动招聘方的项目页，通常不是数量多，而是至少有一个案例能清楚讲出背景、取舍、实现和结果。',
    stack: ['你的技术栈', '你的结果', '你的影响'],
  },
];
