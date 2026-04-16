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
    period: 'Tooling / ongoing',
    category: 'Workflow automation',
    summary:
      'A research workflow toolkit aimed at making experiments, artifacts, and task handoffs easier to organize and revisit.',
    outcome:
      'Useful as a portfolio story about turning internal productivity pain points into a reusable engineering system.',
    stack: ['Python', 'Automation', 'Experiment Ops'],
    href: 'https://github.com/Yichen-Gao/Labflow',
    featured: true,
  },
  {
    title: 'Multimodal Evaluation Workbench',
    period: 'Research project',
    category: 'Benchmarking',
    summary:
      'A portfolio-ready bucket for benchmark design, error analysis, and evaluation scripts around audio or multimodal language systems.',
    outcome:
      'Shows that you can move beyond model demos and build measurement pipelines that expose strengths, blind spots, and failure modes.',
    stack: ['Python', 'Evaluation', 'Data Analysis'],
    featured: true,
  },
  {
    title: 'Research Automation Loop',
    period: 'Internal tooling',
    category: 'Developer experience',
    summary:
      'An automation setup for compressing the loop between idea capture, implementation, experiment tracking, and review-oriented iteration.',
    outcome:
      'Frames your work as end-to-end system thinking rather than isolated notebooks or one-off scripts.',
    stack: ['CLI', 'Prompt Workflows', 'Experiment Tracking'],
    featured: true,
  },
  {
    title: 'Case Study Placeholder',
    period: 'Add one more',
    category: 'Recommended edit',
    summary:
      'Swap this card with your strongest internship, thesis, open-source, or production-facing project before sending the site to recruiters.',
    outcome:
      'The best version of this site has at least one story with clear context, decision-making, technical depth, and measurable results.',
    stack: ['Your stack', 'Your result', 'Your impact'],
  },
];
