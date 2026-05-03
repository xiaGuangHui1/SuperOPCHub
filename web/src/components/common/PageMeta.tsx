import { Helmet, HelmetProvider } from 'react-helmet-async';

interface PageMetaProps {
  title: string;
  description?: string;
  keywords?: string[] | string;
}

export const PageMeta: React.FC<PageMetaProps> = (props) => {
  const { title, description, keywords } = props;
  const keywordsContent = Array.isArray(keywords)
    ? keywords.join(', ')
    : keywords;

  return (
    <Helmet>
      <title>{title}</title>
      <meta name='description' content={description} />
      {!!keywords?.length && <meta name='keywords' content={keywordsContent} />}
    </Helmet>
  );
};

export const HelmetProviderWrapper: React.FC<React.PropsWithChildren> = (
  props,
) => {
  return <HelmetProvider>{props.children}</HelmetProvider>;
};
