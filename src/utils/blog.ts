export const categoryToSlug = (value: string) => {
  const preset: Record<string, string> = {
    网站: 'site',
    项目: 'projects',
    默认: 'general',
  };

  return preset[value] ?? value.toLowerCase().replace(/\s+/g, '-');
};
