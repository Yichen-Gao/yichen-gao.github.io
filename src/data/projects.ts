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
    period: '持续迭代中',
    category: '工作流工具',
    summary: '用于整理实验任务、结果沉淀和协作交接的研究工作流工具。',
    outcome: '这个项目更像系统化工具，而不是一次性的脚本集合。',
    stack: ['Python', 'Automation', 'Experiment Ops'],
    href: 'https://github.com/Yichen-Gao/Labflow',
    featured: true,
  },
  {
    title: '多模态评测工作台',
    period: '研究项目',
    category: '评测分析',
    summary: '围绕多模态任务整理 benchmark、错误分析和评测脚本。',
    outcome: '重点不是模型包装，而是把能力边界和失败模式测清楚。',
    stack: ['Python', 'Evaluation', 'Data Analysis'],
    featured: true,
  },
  {
    title: '研究自动化链路',
    period: '内部工具化',
    category: '效率提升',
    summary: '把想法整理、实现、实验跟踪和回看串成更短的迭代闭环。',
    outcome: '体现的是对流程设计和开发效率的关注。',
    stack: ['CLI', 'Prompt Workflows', 'Experiment Tracking'],
    featured: true,
  },
  {
    title: '待补充项目',
    period: '建议替换',
    category: '占位',
    summary: '这里建议换成你最强的一段真实经历，比如实习、论文项目或开源贡献。',
    outcome: '后续最好补上更具体的背景、实现和结果。',
    stack: ['真实项目', '真实结果'],
  },
];
