export const homeProfile = {
  tagline: '更关心从想法、实验、评测到交付的完整闭环，而不只是一次性的 demo。',
  availability: '目前开放 AI 应用、研究工程、机器学习系统相关机会。',
  statement:
    '主页风格参考学术主页的单页信息架构，但内容仍然围绕我当前真实在做的工程与研究工作来组织。',
  news: [
    {
      date: '2026.06',
      text: '把个人主页改成学术名片风格版本，后续会继续补齐正式简历、代表案例和公开写作。',
    },
    {
      date: '2026.06',
      text: '持续整理多模态评测、语音-文本冲突诊断和研究自动化相关项目，逐步沉淀成可展示资产。',
    },
    {
      date: '2026.06',
      text: '正在找工作，优先关注 AI 应用、研究工程、评测系统和实验基础设施方向。',
    },
  ],
  themes: [
    {
      title: 'AI 应用工程',
      description:
        '把需求拆解、原型实现、工具串联和最终展示放在同一条链路里，关注可迭代性与可维护性。',
      chips: ['Product Thinking', 'Rapid Prototyping', 'Delivery'],
    },
    {
      title: '多模态评测与诊断',
      description:
        '围绕 benchmark、错误分析、干预实验和失败模式总结，尽量把“模型哪里不行”讲清楚。',
      chips: ['Benchmarking', 'Failure Analysis', 'Intervention'],
    },
    {
      title: '研究工程与自动化',
      description:
        '把目录治理、脚本封装、实验回看、交接文档和 agent workflow 做成可复用的基础设施。',
      chips: ['Automation', 'CLI Workflows', 'Experiment Ops'],
    },
  ],
  workstreams: [
    {
      period: '现在',
      title: '个人展示与求职材料升级',
      detail: '把站点、简历、项目说明和博客整理成统一的对外呈现结构。',
    },
    {
      period: '持续',
      title: '研究工作流工具建设',
      detail: '围绕 Labflow 和一系列 agent/CLI 流程，缩短想法到实验再到总结的闭环。',
    },
    {
      period: '持续',
      title: '多模态评测与错误分析',
      detail: '整理 benchmark、脚本与结果，关注语音、文本等任务中的能力边界与失败模式。',
    },
  ],
  resources: [
    {
      title: 'PDF 简历',
      description: '统一入口，便于直接预览或下载正式简历。',
      href: '/resume/',
      cta: '查看简历',
    },
    {
      title: '项目总览',
      description: '集中放代表项目，适合快速浏览我更想强调的工程与研究工作。',
      href: '/projects/',
      cta: '浏览项目',
    },
    {
      title: '博客与方法笔记',
      description: '记录我如何整理项目、站点、工作流和实验复盘。',
      href: '/blog/',
      cta: '进入博客',
    },
  ],
};
